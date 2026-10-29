package flow.audit4;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.springframework.jdbc.core.JdbcTemplate;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Function;
import static org.junit.jupiter.api.Assertions.*;

@Timeout(30)
class StockProbeTest {
    private static final StockProbe.Key KEY = new StockProbe.Key("owner-A", "variant-1", "location-1");
    private final JdbcTemplate jdbc = TestSupport.jdbc();

    @BeforeAll
    static void createIsolatedSchema() {
        JdbcTemplate db = TestSupport.jdbc();
        db.execute("create schema if not exists stock4");
        db.execute("""
            create table if not exists stock4.position (
                owner_id text not null, product_id text not null, location_id text not null,
                physical bigint not null check (physical >= 0),
                reserved bigint not null check (reserved >= 0 and reserved <= physical),
                primary key (owner_id, product_id, location_id)
            )
            """);
        db.execute("""
            create table if not exists stock4.request_result (
                request_id text primary key, payload text not null,
                outcome text, code text, quantity bigint
            )
            """);
        db.execute("""
            create table if not exists stock4.reservation (
                owner_id text not null, product_id text not null, location_id text not null,
                reservation_id text not null, remaining bigint not null check (remaining >= 0),
                state text not null,
                primary key (owner_id, product_id, location_id, reservation_id),
                foreign key (owner_id, product_id, location_id)
                    references stock4.position(owner_id, product_id, location_id)
            )
            """);
        db.execute("""
            create table if not exists stock4.journal (
                id bigserial primary key,
                request_id text not null unique references stock4.request_result(request_id),
                owner_id text not null, product_id text not null, location_id text not null,
                kind text not null, physical_delta bigint not null, reserved_delta bigint not null,
                recorded_at timestamptz not null default clock_timestamp(),
                foreign key (owner_id, product_id, location_id)
                    references stock4.position(owner_id, product_id, location_id)
            )
            """);
    }

    @BeforeEach
    void resetOnlyStockSchema() {
        jdbc.execute("""
            truncate table stock4.journal, stock4.reservation, stock4.request_result,
                stock4.position restart identity
            """);
    }

    @Test
    void twoRequestsForSevenShareTenWithAnObservedDatabaseLockWait() throws Exception {
        seedTen();
        List<StockProbe.Result> results = overlap(
            probe -> probe.execute(command("request-A", StockProbe.Kind.RESERVE, "reserve-A", 7)),
            probe -> probe.execute(command("request-B", StockProbe.Kind.RESERVE, "reserve-B", 7)));
        assertEquals(List.of(3L, 7L), results.stream().map(StockProbe.Result::quantity).sorted().toList());
        assertTrue(results.stream().allMatch(result -> result.outcome().equals("ACCEPTED")));
        assertEquals(2, count("stock4.reservation"));
        assertEquals(3, count("stock4.journal"));
        assertEquals(3, count("stock4.request_result"));
        assertStateAndReconciliation(10, 10);
    }

    @Test
    void concurrentFirstUseMaterializesOneKeyWithoutLosingEitherReceipt() throws Exception {
        List<StockProbe.Result> results = overlap(
            probe -> probe.execute(command("first-receipt", StockProbe.Kind.RECEIVE, null, 5)),
            probe -> probe.execute(command("second-receipt", StockProbe.Kind.RECEIVE, null, 5)));
        assertTrue(results.stream().allMatch(result -> result.outcome().equals("ACCEPTED")));
        assertEquals(1, count("stock4.position"));
        assertEquals(2, count("stock4.journal"));
        assertEquals(2, count("stock4.request_result"));
        assertStateAndReconciliation(10, 0);
    }

    @Test
    void concurrentDuplicateHasOneEffectAndChangedPayloadIsAConflict() throws Exception {
        seedTen();
        StockProbe.Command original = command("same-request", StockProbe.Kind.RESERVE, "reserve-A", 7);
        List<StockProbe.Result> results = overlap(
            probe -> probe.execute(original), probe -> probe.execute(original));
        assertEquals(results.getFirst(), results.getLast());
        assertEquals(new StockProbe.Result("ACCEPTED", "RESERVED", 7), results.getFirst());
        assertEquals(1, count("stock4.reservation"));
        assertEquals(2, count("stock4.journal"));
        assertEquals(2, count("stock4.request_result"));
        assertStateAndReconciliation(10, 7);

        StockProbe probe = new StockProbe();
        StockProbe.Result conflict = probe.execute(
            command("same-request", StockProbe.Kind.RESERVE, "reserve-A", 8));
        assertEquals(new StockProbe.Result("CONFLICT", "REQUEST_KEY_REUSED", 0), conflict);
        assertEquals(results.getFirst(), probe.execute(original));
        assertEquals(2, count("stock4.journal"));
        assertEquals(2, count("stock4.request_result"));
        assertStateAndReconciliation(10, 7);
    }

    @Test
    void technicalFailureBeforeCommitLeavesNoDurableEffectAndCanBeRetried() {
        seedTen();
        StockProbe.Command request = command("retry-after-rollback", StockProbe.Kind.RESERVE, "reserve-A", 7);
        StockProbe failing = new StockProbe(new StockProbe.Hooks() {
            @Override public void beforeCommit() { throw new TechnicalFailure(); }
        });
        assertThrows(TechnicalFailure.class, () -> failing.execute(request));
        assertEquals(0L, jdbc.queryForObject("""
            select count(*) from stock4.request_result where request_id = 'retry-after-rollback'
            """, Long.class));
        assertEquals(0, count("stock4.reservation"));
        assertEquals(1, count("stock4.journal"));
        assertStateAndReconciliation(10, 0);

        assertEquals(new StockProbe.Result("ACCEPTED", "RESERVED", 7),
            new StockProbe().execute(request));
        assertEquals(2, count("stock4.journal"));
        assertEquals(2, count("stock4.request_result"));
        assertStateAndReconciliation(10, 7);
    }

    @Test
    void lostResponseAfterCommitIsReplayedEvenWhenCurrentStateLaterChanges() {
        seedTen();
        StockProbe probe = new StockProbe();
        StockProbe.Command request = command("lost-response", StockProbe.Kind.RESERVE, "reserve-A", 7);
        AtomicReference<StockProbe.Result> committed = new AtomicReference<>();
        // Deliberately outside execute(): execute has returned after the database commit.
        assertThrows(LostResponse.class, () -> {
            committed.set(probe.execute(request));
            throw new LostResponse();
        });
        assertStateAndReconciliation(10, 7);
        assertEquals(committed.get(), probe.execute(request));
        assertEquals(2, count("stock4.journal"));
        assertEquals(2, count("stock4.request_result"));

        probe.execute(command("release-after-loss", StockProbe.Kind.RELEASE, "reserve-A", 0));
        assertEquals(committed.get(), probe.execute(request));
        assertEquals(3, count("stock4.journal"));
        assertEquals(3, count("stock4.request_result"));
        assertStateAndReconciliation(10, 0);
    }

    @Test
    void consumeThenRefuseCompensationRetainRefusalAndAcceptNewIntentionAfterRelease() {
        seedTen();
        StockProbe probe = new StockProbe();
        probe.execute(command("reserve-six", StockProbe.Kind.RESERVE, "reserve-A", 6));
        probe.execute(command("consume-two", StockProbe.Kind.CONSUME, "reserve-A", 2));
        assertStateAndReconciliation(8, 4);
        assertEquals(4L, jdbc.queryForObject("select remaining from stock4.reservation", Long.class));
        assertEquals(3, count("stock4.journal"));

        StockProbe.Command refusedIntention = command("compensate-before-release",
            StockProbe.Kind.CORRECT, null, -5);
        StockProbe.Result refused = probe.execute(refusedIntention);
        assertEquals(new StockProbe.Result("REJECTED", "CORRECTION_BELOW_RESERVED", 0), refused);
        assertEquals("REJECTED", jdbc.queryForObject("""
            select outcome from stock4.request_result where request_id = 'compensate-before-release'
            """, String.class));
        assertEquals(3, count("stock4.journal"));
        assertStateAndReconciliation(8, 4);

        assertEquals(new StockProbe.Result("ACCEPTED", "RELEASED", 4),
            probe.execute(command("release-four", StockProbe.Kind.RELEASE, "reserve-A", 0)));
        assertStateAndReconciliation(8, 0);
        assertEquals(refused, probe.execute(refusedIntention));
        assertEquals(4, count("stock4.journal"));
        assertStateAndReconciliation(8, 0);

        assertEquals(new StockProbe.Result("ACCEPTED", "CORRECTED", -5),
            probe.execute(command("compensate-new-intention", StockProbe.Kind.CORRECT, null, -5)));
        assertEquals(5, count("stock4.journal"));
        assertEquals(6, count("stock4.request_result"));
        assertEquals("RELEASED", jdbc.queryForObject("select state from stock4.reservation", String.class));
        // Original facts are retained; compensation adds a journal entry.
        assertEquals(10L, jdbc.queryForObject("""
            select physical_delta from stock4.journal where request_id = 'initial-receipt'
            """, Long.class));
        assertStateAndReconciliation(3, 0);
    }

    private void seedTen() {
        assertEquals(new StockProbe.Result("ACCEPTED", "RECEIVED", 10),
            new StockProbe().execute(command("initial-receipt", StockProbe.Kind.RECEIVE, null, 10)));
    }

    private static StockProbe.Command command(String id, StockProbe.Kind kind,
                                               String reservationId, long quantity) {
        return new StockProbe.Command(id, kind, KEY, reservationId, quantity);
    }

    private int count(String table) {
        // The caller supplies only literal schema-qualified test table names.
        return jdbc.queryForObject("select count(*) from " + table, Integer.class);
    }

    private void assertStateAndReconciliation(long physical, long reserved) {
        StockProbe.Position state = jdbc.queryForObject("""
            select physical, reserved from stock4.position
            where owner_id = ? and product_id = ? and location_id = ?
            """, (rs, row) -> new StockProbe.Position(rs.getLong(1), rs.getLong(2)),
            KEY.owner(), KEY.product(), KEY.location());
        assertNotNull(state);
        assertEquals(physical, state.physical());
        assertEquals(reserved, state.reserved());
        assertEquals(physical - reserved, state.physical() - state.reserved());
        assertEquals(physical, jdbc.queryForObject("""
            select coalesce(sum(physical_delta), 0) from stock4.journal
            """, Long.class));
        assertEquals(reserved, jdbc.queryForObject("""
            select coalesce(sum(reserved_delta), 0) from stock4.journal
            """, Long.class));
        assertEquals(reserved, jdbc.queryForObject("""
            select coalesce(sum(remaining), 0) from stock4.reservation
            """, Long.class));
        assertTrue(state.physical() >= state.reserved() && state.reserved() >= 0);
        System.out.printf("STOCK4 reconciled physical=%d reserved=%d available=%d journal=%d%n",
            physical, reserved, physical - reserved, count("stock4.journal"));
    }

    private List<StockProbe.Result> overlap(Function<StockProbe, StockProbe.Result> first,
                                            Function<StockProbe, StockProbe.Result> second) throws Exception {
        CountDownLatch firstLocked = new CountDownLatch(1);
        CountDownLatch releaseFirst = new CountDownLatch(1);
        CountDownLatch secondBegan = new CountDownLatch(1);
        AtomicInteger firstPid = new AtomicInteger();
        AtomicInteger secondPid = new AtomicInteger();
        StockProbe firstProbe = new StockProbe(new StockProbe.Hooks() {
            @Override public void afterTransactionBegin(int pid) { firstPid.set(pid); }
            @Override public void afterPositionLocked() {
                firstLocked.countDown();
                await(releaseFirst);
            }
        });
        StockProbe secondProbe = new StockProbe(new StockProbe.Hooks() {
            @Override public void afterTransactionBegin(int pid) {
                secondPid.set(pid);
                secondBegan.countDown();
            }
        });
        ExecutorService executor = Executors.newFixedThreadPool(2);
        try {
            Future<StockProbe.Result> firstResult = executor.submit(() -> first.apply(firstProbe));
            assertTrue(firstLocked.await(10, TimeUnit.SECONDS), "First transaction did not acquire its lock");
            Future<StockProbe.Result> secondResult = executor.submit(() -> second.apply(secondProbe));
            assertTrue(secondBegan.await(10, TimeUnit.SECONDS), "Second transaction did not begin");
            assertNotEquals(firstPid.get(), secondPid.get(), "Transactions must use distinct connections");
            long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
            boolean lockWaitObserved = false;
            while (System.nanoTime() < deadline) {
                lockWaitObserved = Boolean.TRUE.equals(jdbc.queryForObject("""
                    select exists (
                        select 1 from pg_stat_activity where pid = ? and wait_event_type = 'Lock'
                    )
                    """, Boolean.class, secondPid.get()));
                if (lockWaitObserved) break;
                Thread.sleep(10);
            }
            assertTrue(lockWaitObserved, "Second connection never visibly waited on a PostgreSQL lock");
            assertFalse(secondResult.isDone(), "Second transaction completed while first held the conflicting lock");
            System.out.printf("STOCK4 concurrent sessions=%d,%d PostgreSQL lock wait observed%n",
                firstPid.get(), secondPid.get());
            releaseFirst.countDown();
            return List.of(firstResult.get(10, TimeUnit.SECONDS), secondResult.get(10, TimeUnit.SECONDS));
        } finally {
            releaseFirst.countDown();
            executor.shutdownNow();
            assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS), "Concurrent workers did not finish");
        }
    }

    private static void await(CountDownLatch latch) {
        try {
            if (!latch.await(15, TimeUnit.SECONDS)) throw new IllegalStateException("Test latch timed out");
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Test latch interrupted", interrupted);
        }
    }

    private static final class TechnicalFailure extends RuntimeException {}
    private static final class LostResponse extends RuntimeException {}
}