package flow.audit4;

/** Separate JVM so Runtime.halt does not become an exception caught by Spring. */
public final class RefProbeWorker {
    public static void main(String[] args) {
        String batch = args[0], mode = args[1];
        int stop = Integer.parseInt(args[2]);
        new RefProbe().drain(batch,
                count -> { if (mode.equals("after") && count == stop) Runtime.getRuntime().halt(91); },
                () -> { if (mode.equals("inside")) Runtime.getRuntime().halt(92); });
        System.out.println("REF worker finished persisted batch");
        System.exit(0);
    }
}
