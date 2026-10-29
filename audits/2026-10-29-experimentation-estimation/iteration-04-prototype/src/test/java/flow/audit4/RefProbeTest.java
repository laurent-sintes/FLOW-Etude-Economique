package flow.audit4;

import static org.junit.jupiter.api.Assertions.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;

public class RefProbeTest {
    private JdbcTemplate jdbc;
    @BeforeEach void cleanOwnSchema() { RefProbe.resetSchema(); jdbc = TestSupport.jdbc(); }

    private String stage(String... rows) throws Exception {
        return new RefProbe().stage((RefProbe.HEADER + "\n" + String.join("\n", rows) + "\n")
                .getBytes(StandardCharsets.UTF_8));
    }
    private long count(String query, Object... args) { return jdbc.queryForObject(query, Long.class, args); }
    private long state(String batch, String state) {
        return count("SELECT count(*) FROM ref4.line WHERE batch_id=? AND state=?", batch, state);
    }
    private String row(String kind, String id, long version, String parent, String name) {
        return RefProbe.row(kind, "ERP", id, version, parent, name);
    }
    private int worker(String batch, String mode, int stop) throws Exception {
        String java = Path.of(System.getProperty("java.home"), "bin",
                System.getProperty("os.name").startsWith("Windows") ? "java.exe" : "java").toString();
        String cp = System.getProperty("surefire.test.class.path", System.getProperty("java.class.path"));
        Path logs = Path.of("target", "ref-worker-logs").toAbsolutePath();
        Files.createDirectories(logs);
        Path log = Files.createTempFile(logs, "ref-worker-" + mode + "-", ".log");
        Process process = new ProcessBuilder(java, "-cp", cp, "flow.audit4.RefProbeWorker",
                batch, mode, Integer.toString(stop)).redirectErrorStream(true).redirectOutput(log.toFile()).start();
        try {
            if (!process.waitFor(900, TimeUnit.SECONDS)) {
                process.destroyForcibly().onExit().join();
                fail("REF worker exceeded the 900 s witness timeout; no performance guarantee inferred. "
                        + workerLog(log));
            }
            int expected = switch (mode) { case "after" -> 91; case "inside" -> 92; default -> 0; };
            int actual = process.exitValue();
            assertEquals(expected, actual, () -> workerLog(log));
            return actual;
        } finally {
            if (process.isAlive()) process.destroyForcibly().onExit().join();
        }
    }
    private String workerLog(Path log) {
        try {
            String output = Files.readString(log, StandardCharsets.UTF_8);
            if (output.length() > 8000) output = output.substring(output.length() - 8000);
            return "Worker log retained at " + log + "\n" + output;
        } catch (IOException e) {
            return "Worker log retained at " + log + "; could not read it: " + e.getMessage();
        }
    }

    @Test void tenThousandRowsRecoverAcrossRealJvmTermination() throws Exception {
        StringBuilder csv = new StringBuilder(RefProbe.HEADER).append('\n');
        for (int i = 0; i < 5000; i++) {
            csv.append(row("V", "V" + i, 1, "P" + i, "Variante " + i)).append('\n');
            csv.append(row("P", "P" + i, 1, "", "Produit été " + i)).append('\n');
        }
        String batch = new RefProbe().stage(csv.toString().getBytes(StandardCharsets.UTF_8));
        assertEquals(91, worker(batch, "after", 211));
        assertEquals(211, state(batch, "ACCEPTED"));
        assertEquals(9789, state(batch, "PENDING"));
        assertEquals(211, count("SELECT count(*) FROM ref4.effect"));
        assertEquals(211, count("SELECT count(*) FROM ref4.object"));
        assertEquals(211, count("SELECT processed FROM ref4.batch WHERE id=?", batch));
        assertEquals("RUNNING", jdbc.queryForObject("SELECT state FROM ref4.batch WHERE id=?", String.class, batch));
        assertEquals(0, worker(batch, "resume", 0));
        assertEquals(10000, state(batch, "ACCEPTED"));
        assertEquals(0, state(batch, "PENDING"));
        assertEquals(10000, count("SELECT count(*) FROM ref4.object"));
        assertEquals(10000, count("SELECT count(*) FROM ref4.effect"));
        assertEquals(10000, count("SELECT sum(applications) FROM ref4.object"));
        assertEquals(10000, count("SELECT processed FROM ref4.batch WHERE id=?", batch));
        assertEquals("\u001fProduit été 4999" + "\u001f".repeat(11), jdbc.queryForObject(
                "SELECT payload FROM ref4.object WHERE kind='P' AND external_id='P4999'", String.class));
        assertEquals(0, count("SELECT count(*) FROM ref4.object v LEFT JOIN ref4.object p "
                + "ON p.kind='P' AND p.external_id=v.parent_id WHERE v.kind='V' AND p.external_id IS NULL"));
        assertEquals("DONE", jdbc.queryForObject("SELECT state FROM ref4.batch WHERE id=?", String.class, batch));
        new RefProbe().drain(batch);
        assertEquals(10000, count("SELECT sum(applications) FROM ref4.object"));
        assertEquals(10000, count("SELECT count(*) FROM ref4.effect"));
    }

    @Test void crashInsideLineRollsBackObjectAndDurableLineTogether() throws Exception {
        String batch = stage(row("P", "P1", 1, "", "Un"), row("P", "P2", 1, "", "Deux"));
        assertEquals(92, worker(batch, "inside", 0));
        assertEquals(0, count("SELECT count(*) FROM ref4.object"));
        assertEquals(0, count("SELECT count(*) FROM ref4.effect"));
        assertEquals(2, state(batch, "PENDING"));
        assertEquals(0, count("SELECT processed FROM ref4.batch WHERE id=?", batch));
        assertEquals(0, worker(batch, "resume", 0));
        assertEquals(2, state(batch, "ACCEPTED"));
        assertEquals(2, count("SELECT sum(applications) FROM ref4.object"));
    }

    @Test void rejectedVariantIsDurableAndOnlyCorrectedContributionIsReplayed() throws Exception {
        String original = stage(row("V", "V1", 1, "MISSING", "Variante"),
                row("P", "P1", 1, "", "Produit, \"été\""));
        new RefProbe().drain(original);
        assertEquals(1, state(original, "ACCEPTED"));
        assertEquals(1, state(original, "REJECTED"));
        assertEquals("\u001fProduit, \"été\"" + "\u001f".repeat(11), jdbc.queryForObject(
                "SELECT payload FROM ref4.object WHERE kind='P' AND external_id='P1'", String.class));
        assertEquals("MISSING_PARENT", jdbc.queryForObject("SELECT reason FROM ref4.line "
                + "WHERE batch_id=? AND line_no=1", String.class, original));
        String corrected = stage(row("V", "V1", 1, "P1", "Variante"));
        new RefProbe().drain(corrected);
        assertEquals(1, state(corrected, "ACCEPTED"));
        assertEquals(1, count("SELECT count(*) FROM ref4.line WHERE batch_id=?", corrected));
        assertEquals(1, state(original, "REJECTED"));
        assertEquals(1, count("SELECT applications FROM ref4.object WHERE kind='P' AND external_id='P1'"));
        assertEquals(2, count("SELECT count(*) FROM ref4.object"));
        assertEquals(2, count("SELECT count(*) FROM ref4.effect"));
    }

    @Test void versionAuthorityAndAbsentObjectsHaveExplicitOutcomes() throws Exception {
        String first = stage(row("P", "P1", 1, "", "Premier"), row("P", "KEEP", 1, "", "Absent ensuite"));
        new RefProbe().drain(first);
        String newer = stage(row("P", "P1", 2, "", "Deuxième"));
        new RefProbe().drain(newer);
        String checks = stage(row("P", "P1", 2, "", "Deuxième"), row("P", "P1", 2, "", "Conflit"),
                row("P", "P1", 1, "", "Premier"), RefProbe.row("P", "OTHER", "P1", 3, "", "Autre source"));
        new RefProbe().drain(checks);
        assertEquals(1, state(checks, "IGNORED"));
        assertEquals(3, state(checks, "REJECTED"));
        assertEquals(1, count("SELECT count(*) FROM ref4.line WHERE batch_id=? AND reason='VERSION_CONFLICT'", checks));
        assertEquals(1, count("SELECT count(*) FROM ref4.line WHERE batch_id=? AND reason='OLDER_VERSION'", checks));
        assertEquals(1, count("SELECT count(*) FROM ref4.line WHERE batch_id=? AND reason='AUTHORITY_CONFLICT'", checks));
        assertEquals(2, count("SELECT version FROM ref4.object WHERE kind='P' AND external_id='P1'"));
        assertEquals(2, count("SELECT applications FROM ref4.object WHERE kind='P' AND external_id='P1'"));
        assertEquals(1, count("SELECT count(*) FROM ref4.object WHERE external_id='KEEP'"));
        assertEquals(3, count("SELECT sum(applications) FROM ref4.object"));
    }

    @Test void malformedLineDoesNotPreventFollowingValidLine() throws Exception {
        String batch = stage("V,ERP,broken", row("P", "P1", 1, "", "Valide"), row("P", "EMPTY", 1, "", ""));
        new RefProbe().drain(batch);
        assertEquals(1, state(batch, "ACCEPTED"));
        assertEquals(2, state(batch, "REJECTED"));
        assertEquals(1, count("SELECT count(*) FROM ref4.object"));
        assertEquals(2, count("SELECT count(*) FROM ref4.line WHERE batch_id=? AND reason IS NOT NULL AND state='REJECTED'", batch));
    }
}
