package flow.audit4;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.support.TransactionTemplate;
import java.util.List;
import java.util.Objects;

/**
 * Bounded design witness, not a product implementation or an effort measurement.
 * One local PostgreSQL transaction, one stock key, integral quantities in one fixed unit.
 * COMMON-like request persistence is included only to exercise its composition with STOCK.
 */
final class StockProbe {
    record Key(String owner, String product, String location) {
        Key {
            Objects.requireNonNull(owner);
            Objects.requireNonNull(product);
            Objects.requireNonNull(location);
        }
    }
    enum Kind { RECEIVE, RESERVE, CONSUME, RELEASE, CORRECT }
    record Command(String requestId, Kind kind, Key key, String reservationId, long quantity) {
        Command {
            Objects.requireNonNull(requestId);
            Objects.requireNonNull(kind);
            Objects.requireNonNull(key);
        }
        String payload() {
            return part(kind.name()) + part(key.owner()) + part(key.product())
                + part(key.location()) + part(reservationId) + part(Long.toString(quantity));
        }
        private static String part(String value) {
            return value == null ? "-1:" : value.length() + ":" + value;
        }
    }
    record Result(String outcome, String code, long quantity) {}
    record Position(long physical, long reserved) {}
    private record Request(String payload, Result result) {}
    interface Hooks {
        default void afterTransactionBegin(int backendPid) {}
        default void afterPositionLocked() {}
        default void beforeCommit() {}
    }

    private final JdbcTemplate jdbc;
    private final TransactionTemplate tx;
    private final Hooks hooks;

    StockProbe() {
        this(new Hooks() {});
    }
    StockProbe(Hooks hooks) {
        this.jdbc = TestSupport.jdbc();
        this.tx = TestSupport.tx();
        this.hooks = hooks;
    }

    Result execute(Command command) {
        return Objects.requireNonNull(tx.execute(transaction -> {
            hooks.afterTransactionBegin(jdbc.queryForObject("select pg_backend_pid()", Integer.class));
            jdbc.update("""
                insert into stock4.request_result(request_id, payload)
                values (?, ?) on conflict (request_id) do nothing
                """, command.requestId(), command.payload());
            Request prior = jdbc.queryForObject("""
                select payload, outcome, code, quantity from stock4.request_result
                where request_id = ? for update
                """, (rs, row) -> new Request(rs.getString("payload"),
                    rs.getString("outcome") == null ? null
                        : new Result(rs.getString("outcome"), rs.getString("code"),
                                     rs.getLong("quantity"))), command.requestId());
            if (!prior.payload().equals(command.payload())) {
                return new Result("CONFLICT", "REQUEST_KEY_REUSED", 0);
            }
            if (prior.result() != null) {
                return prior.result();
            }

            Key key = command.key();
            // SELECT FOR UPDATE cannot lock a nonexistent key: establish the unique row first.
            jdbc.update("""
                insert into stock4.position(owner_id, product_id, location_id, physical, reserved)
                values (?, ?, ?, 0, 0)
                on conflict (owner_id, product_id, location_id) do nothing
                """, key.owner(), key.product(), key.location());
            Position position = jdbc.queryForObject("""
                select physical, reserved from stock4.position
                where owner_id = ? and product_id = ? and location_id = ? for update
                """, (rs, row) -> new Position(rs.getLong("physical"), rs.getLong("reserved")),
                key.owner(), key.product(), key.location());
            hooks.afterPositionLocked();
            Result result = apply(command, position);
            jdbc.update("""
                update stock4.request_result set outcome = ?, code = ?, quantity = ?
                where request_id = ?
                """, result.outcome(), result.code(), result.quantity(), command.requestId());
            // Injection point after all effects, including the durable response, but before commit.
            hooks.beforeCommit();
            return result;
        }));
    }

    private Result apply(Command command, Position position) {
        return switch (command.kind()) {
            case RECEIVE -> {
                if (command.quantity() <= 0) yield rejected("POSITIVE_QUANTITY_REQUIRED");
                change(command, position, command.quantity(), 0);
                yield accepted("RECEIVED", command.quantity());
            }
            case RESERVE -> {
                if (command.reservationId() == null || command.quantity() <= 0) {
                    yield rejected("VALID_RESERVATION_REQUIRED");
                }
                if (remaining(command) != null) yield rejected("RESERVATION_ALREADY_EXISTS");
                long granted = Math.min(command.quantity(), position.physical() - position.reserved());
                if (granted == 0) yield rejected("NO_AVAILABLE_STOCK");
                Key key = command.key();
                jdbc.update("""
                    insert into stock4.reservation
                    (owner_id, product_id, location_id, reservation_id, remaining, state)
                    values (?, ?, ?, ?, ?, 'OPEN')
                    """, key.owner(), key.product(), key.location(), command.reservationId(), granted);
                change(command, position, 0, granted);
                yield accepted(granted < command.quantity() ? "PARTIALLY_RESERVED" : "RESERVED", granted);
            }
            case CONSUME -> {
                Long outstanding = remaining(command);
                if (outstanding == null) yield rejected("RESERVATION_NOT_FOUND");
                if (command.quantity() <= 0 || command.quantity() > outstanding) {
                    yield rejected("INVALID_CONSUMPTION");
                }
                long after = outstanding - command.quantity();
                updateReservation(command, after, after == 0 ? "CONSUMED" : "OPEN");
                change(command, position, -command.quantity(), -command.quantity());
                yield accepted("CONSUMED", command.quantity());
            }
            case RELEASE -> {
                Long outstanding = remaining(command);
                if (outstanding == null) yield rejected("RESERVATION_NOT_FOUND");
                if (outstanding == 0) yield rejected("RESERVATION_ALREADY_CLOSED");
                updateReservation(command, 0, "RELEASED");
                change(command, position, 0, -outstanding);
                yield accepted("RELEASED", outstanding);
            }
            case CORRECT -> {
                long corrected = Math.addExact(position.physical(), command.quantity());
                if (corrected < 0 || corrected < position.reserved()) {
                    yield rejected("CORRECTION_BELOW_RESERVED");
                }
                change(command, position, command.quantity(), 0);
                yield accepted("CORRECTED", command.quantity());
            }
        };
    }

    private Long remaining(Command command) {
        Key key = command.key();
        List<Long> matches = jdbc.query("""
            select remaining from stock4.reservation
            where owner_id = ? and product_id = ? and location_id = ? and reservation_id = ?
            """, (rs, row) -> rs.getLong(1), key.owner(), key.product(), key.location(),
            command.reservationId());
        return matches.isEmpty() ? null : matches.getFirst();
    }

    private void updateReservation(Command command, long remaining, String state) {
        Key key = command.key();
        jdbc.update("""
            update stock4.reservation set remaining = ?, state = ?
            where owner_id = ? and product_id = ? and location_id = ? and reservation_id = ?
            """, remaining, state, key.owner(), key.product(), key.location(), command.reservationId());
    }

    private void change(Command command, Position before, long physicalDelta, long reservedDelta) {
        long physical = Math.addExact(before.physical(), physicalDelta);
        long reserved = Math.addExact(before.reserved(), reservedDelta);
        if (physical < 0 || reserved < 0 || reserved > physical) {
            throw new IllegalStateException("Stock invariant violated");
        }
        Key key = command.key();
        jdbc.update("""
            update stock4.position set physical = ?, reserved = ?
            where owner_id = ? and product_id = ? and location_id = ?
            """, physical, reserved, key.owner(), key.product(), key.location());
        jdbc.update("""
            insert into stock4.journal
            (request_id, owner_id, product_id, location_id, kind, physical_delta, reserved_delta)
            values (?, ?, ?, ?, ?, ?, ?)
            """, command.requestId(), key.owner(), key.product(), key.location(), command.kind().name(),
            physicalDelta, reservedDelta);
    }

    private static Result accepted(String code, long quantity) {
        return new Result("ACCEPTED", code, quantity);
    }
    private static Result rejected(String code) {
        return new Result("REJECTED", code, 0);
    }
}