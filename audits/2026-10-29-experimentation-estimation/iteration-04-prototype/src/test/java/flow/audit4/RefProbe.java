package flow.audit4;

import java.nio.ByteBuffer;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.IntConsumer;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.support.TransactionTemplate;

/** Bounded JDBC witness, not a batch framework or a production importer.
 * One import worker. Canonical CSV has one physical record per line; embedded
 * newlines and control separators are excluded. Authority is fixed on creation.
 */
public final class RefProbe {
    public static final String HEADER = "kind,source,external_id,version,parent_id,"
            + "f01,f02,f03,f04,f05,f06,f07,f08,f09,f10,f11,f12";
    private final JdbcTemplate jdbc = TestSupport.jdbc();
    private final TransactionTemplate tx = TestSupport.tx();

    public static void resetSchema() {
        JdbcTemplate j = TestSupport.jdbc();
        j.execute("DROP SCHEMA IF EXISTS ref4 CASCADE");
        j.execute("CREATE SCHEMA ref4");
        j.execute("CREATE TABLE ref4.batch (id text PRIMARY KEY, state text NOT NULL, "
                + "total_lines integer NOT NULL, processed integer NOT NULL DEFAULT 0)");
        j.execute("CREATE TABLE ref4.object (kind text NOT NULL, external_id text NOT NULL, "
                + "source text NOT NULL, version bigint NOT NULL, parent_id text, payload text NOT NULL, "
                + "applications integer NOT NULL, PRIMARY KEY(kind, external_id))");
        j.execute("CREATE TABLE ref4.line (batch_id text REFERENCES ref4.batch(id), line_no integer, "
                + "raw_csv text NOT NULL, kind text, source text, external_id text, version bigint, "
                + "parent_id text, payload text, validation_error text, state text NOT NULL, reason text, "
                + "PRIMARY KEY(batch_id,line_no))");
        j.execute("CREATE TABLE ref4.effect (batch_id text, line_no integer, kind text NOT NULL, "
                + "external_id text NOT NULL, version bigint NOT NULL, PRIMARY KEY(batch_id,line_no), "
                + "FOREIGN KEY(batch_id,line_no) REFERENCES ref4.line(batch_id,line_no))");
    }

    public String stage(byte[] utf8) throws Exception {
        String text = StandardCharsets.UTF_8.newDecoder()
                .onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT)
                .decode(ByteBuffer.wrap(utf8)).toString();
        String[] records = text.split("\\r?\\n", -1);
        if (records.length == 0 || !HEADER.equals(records[0])) {
            throw new IllegalArgumentException("Canonical CSV header required");
        }
        int end = records.length;
        if (end > 1 && records[end - 1].isEmpty()) end--;
        String batch = UUID.randomUUID().toString();
        List<Object[]> rows = new ArrayList<>();
        for (int i = 1; i < end; i++) {
            Parsed p = parse(records[i]);
            rows.add(new Object[]{batch, i, records[i], p.kind, p.source, p.id,
                    p.version, p.parent, p.payload, p.error, "PENDING"});
        }
        tx.executeWithoutResult(s -> {
            jdbc.update("INSERT INTO ref4.batch (id,state,total_lines) VALUES (?, 'STAGED',?)", batch, rows.size());
            jdbc.batchUpdate("INSERT INTO ref4.line (batch_id,line_no,raw_csv,kind,source,external_id,"
                    + "version,parent_id,payload,validation_error,state) VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows);
        });
        return batch;
    }

    public void drain(String batch) {
        drain(batch, ignored -> {}, () -> {});
    }

    // Hooks are fault injection only. No in-memory cursor is used for recovery.
    public void drain(String batch, IntConsumer afterCommit, Runnable afterObjectMutation) {
        if (jdbc.update("UPDATE ref4.batch SET state='RUNNING' WHERE id=?", batch) != 1) {
            throw new IllegalArgumentException("Unknown batch");
        }
        int committed = 0;
        while (Boolean.TRUE.equals(tx.execute(s -> processNext(batch, afterObjectMutation)))) {
            afterCommit.accept(++committed);
        }
        tx.executeWithoutResult(s -> jdbc.update("UPDATE ref4.batch SET state='DONE' WHERE id=? "
                + "AND NOT EXISTS (SELECT 1 FROM ref4.line WHERE batch_id=? AND state='PENDING')", batch, batch));
    }

    private boolean processNext(String batch, Runnable afterObjectMutation) {
        List<Map<String, Object>> lines = jdbc.queryForList("SELECT * FROM ref4.line "
                + "WHERE batch_id=? AND state='PENDING' ORDER BY "
                + "CASE kind WHEN 'P' THEN 0 WHEN 'V' THEN 1 ELSE 2 END, line_no LIMIT 1 FOR UPDATE", batch);
        if (lines.isEmpty()) return false;
        Map<String, Object> line = lines.getFirst();
        int number = ((Number) line.get("line_no")).intValue();
        String error = (String) line.get("validation_error");
        if (error != null) {
            finish(batch, number, "REJECTED", error);
            return true;
        }
        String kind = (String) line.get("kind"), id = (String) line.get("external_id");
        String source = (String) line.get("source"), parent = (String) line.get("parent_id");
        String payload = (String) line.get("payload");
        long version = ((Number) line.get("version")).longValue();
        if (kind.equals("V") && jdbc.queryForObject("SELECT count(*) FROM ref4.object "
                + "WHERE kind='P' AND external_id=? AND source=?", Long.class, parent, source) == 0) {
            finish(batch, number, "REJECTED", "MISSING_PARENT");
            return true;
        }
        List<Map<String, Object>> objects = jdbc.queryForList("SELECT * FROM ref4.object "
                + "WHERE kind=? AND external_id=?", kind, id);
        if (!objects.isEmpty()) {
            Map<String, Object> old = objects.getFirst();
            long oldVersion = ((Number) old.get("version")).longValue();
            if (!source.equals(old.get("source"))) {
                finish(batch, number, "REJECTED", "AUTHORITY_CONFLICT");
                return true;
            }
            if (version < oldVersion) {
                finish(batch, number, "REJECTED", "OLDER_VERSION");
                return true;
            }
            if (version == oldVersion) {
                boolean same = payload.equals(old.get("payload"));
                finish(batch, number, same ? "IGNORED" : "REJECTED", same ? "IDENTICAL" : "VERSION_CONFLICT");
                return true;
            }
            jdbc.update("UPDATE ref4.object SET version=?,parent_id=?,payload=?,applications=applications+1 "
                    + "WHERE kind=? AND external_id=?", version, parent, payload, kind, id);
        } else {
            jdbc.update("INSERT INTO ref4.object VALUES (?,?,?,?,?,?,1)", kind, id, source, version, parent, payload);
        }
        afterObjectMutation.run();
        jdbc.update("INSERT INTO ref4.effect VALUES (?,?,?,?,?)", batch, number, kind, id, version);
        finish(batch, number, "ACCEPTED", "APPLIED");
        return true;
    }

    private void finish(String batch, int line, String state, String reason) {
        if (jdbc.update("UPDATE ref4.line SET state=?,reason=? WHERE batch_id=? AND line_no=? "
                + "AND state='PENDING'", state, reason, batch, line) != 1) {
            throw new IllegalStateException("Line changed outside the single worker");
        }
        jdbc.update("UPDATE ref4.batch SET processed=processed+1 WHERE id=?", batch);
    }

    private record Parsed(String kind, String source, String id, Long version, String parent,
                          String payload, String error) {}

    private static Parsed parse(String raw) {
        try {
            List<String> c = csv(raw);
            if (c.size() != 17) throw new IllegalArgumentException("FIELD_COUNT");
            String kind = c.get(0), source = c.get(1), id = c.get(2), parent = c.get(4);
            if (!kind.equals("P") && !kind.equals("V")) throw new IllegalArgumentException("TYPE");
            for (String identity : List.of(source, id)) {
                if (!identity.matches("[A-Za-z0-9._-]{1,80}")) throw new IllegalArgumentException("IDENTITY");
            }
            long version;
            try { version = Long.parseLong(c.get(3)); }
            catch (NumberFormatException e) { throw new IllegalArgumentException("VERSION"); }
            if (version < 1) throw new IllegalArgumentException("VERSION");
            if (kind.equals("P") && !parent.isEmpty()) throw new IllegalArgumentException("PRODUCT_PARENT");
            if (kind.equals("V") && !parent.matches("[A-Za-z0-9._-]{1,80}")) throw new IllegalArgumentException("PARENT");
            if (c.get(5).isBlank()) throw new IllegalArgumentException("REQUIRED_NAME");
            for (int i = 5; i < c.size(); i++) {
                String value = c.get(i);
                if (value.length() > 2000 || value.indexOf('\u001f') >= 0 || value.indexOf('\r') >= 0)
                    throw new IllegalArgumentException("SCALAR");
                if (kind.equals("V") && i >= 13 && !value.isEmpty()) throw new IllegalArgumentException("VARIANT_MAX_8");
            }
            return new Parsed(kind, source, id, version, parent, String.join("\u001f", c.subList(4, 17)), null);
        } catch (IllegalArgumentException e) {
            return new Parsed(null, null, null, null, null, null, e.getMessage());
        }
    }

    private static List<String> csv(String raw) {
        List<String> cells = new ArrayList<>();
        StringBuilder cell = new StringBuilder();
        boolean quoted = false, closed = false;
        for (int i = 0; i < raw.length(); i++) {
            char ch = raw.charAt(i);
            if (quoted) {
                if (ch == '"') {
                    if (i + 1 < raw.length() && raw.charAt(i + 1) == '"') { cell.append('"'); i++; }
                    else { quoted = false; closed = true; }
                } else cell.append(ch);
            } else if (ch == ',') {
                cells.add(cell.toString()); cell.setLength(0); closed = false;
            } else if (ch == '"' && cell.isEmpty() && !closed) quoted = true;
            else if (ch == '"' || closed) throw new IllegalArgumentException("CSV_QUOTING");
            else cell.append(ch);
        }
        if (quoted) throw new IllegalArgumentException("CSV_QUOTING");
        cells.add(cell.toString());
        return cells;
    }

    public static String row(String kind, String source, String id, long version, String parent, String name) {
        String[] cells = new String[17];
        Arrays.fill(cells, "");
        cells[0] = kind; cells[1] = source; cells[2] = id; cells[3] = Long.toString(version);
        cells[4] = parent; cells[5] = name;
        return Arrays.stream(cells).map(c -> "\"" + c.replace("\"", "\"\"") + "\"")
                .collect(java.util.stream.Collectors.joining(","));
    }
}
