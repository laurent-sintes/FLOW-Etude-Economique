package flow.trial;
import static org.junit.jupiter.api.Assertions.*;
import static flow.trial.ModelRuntime.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.temporal.client.*;
import io.temporal.testing.*;
import io.temporal.worker.*;
import io.temporal.common.WorkflowExecutionHistory;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.nio.file.*;
import org.junit.jupiter.api.*;
import org.springframework.context.annotation.*;

@Timeout(45)
class TemporalTrialTest {
 TestWorkflowEnvironment env;Actions actions;WorkflowClient client;
 final Path output=Path.of("../results/temporal");
 @Configuration static class Wiring {@Bean Actions actions(){return new Actions();}}
 AnnotationConfigApplicationContext spring;
 @BeforeEach void setup()throws Exception{spring=new AnnotationConfigApplicationContext(Wiring.class);actions=spring.getBean(Actions.class);env=TestWorkflowEnvironment.newInstance(TestEnvironmentOptions.newBuilder().setWorkerFactoryOptions(WorkerFactoryOptions.newBuilder().setWorkflowCacheSize(0).build()).build());Worker worker=env.newWorker("trial");worker.registerWorkflowImplementationTypes(Interpreter.class);worker.registerActivitiesImplementations(actions);env.start();client=env.getWorkflowClient();Files.createDirectories(output);}
 @AfterEach void close(){env.close();spring.close();}
 ModelWorkflow start(String id,Definition def,String mode){ModelWorkflow w=client.newWorkflowStub(ModelWorkflow.class,WorkflowOptions.newBuilder().setTaskQueue("trial").setWorkflowId(id).build());WorkflowClient.start(w::run,def,new CaseInput(def.organisation(),id,mode));await(w,"WAITING");return w;}
 void await(ModelWorkflow w,String state){long end=System.nanoTime()+Duration.ofSeconds(10).toNanos();while(System.nanoTime()<end){try{if(state.equals(w.state().state()))return;}catch(Exception ignored){}try{Thread.sleep(5);}catch(Exception e){throw new RuntimeException(e);}}fail("state not reached "+state);}
 void approve(ModelWorkflow w,String org){w.complete(new Outcome("answer-1",org,"validation","gestionnaire",true));}
 Result result(ModelWorkflow w){try{return WorkflowStub.fromTyped(w).getResult(20,TimeUnit.SECONDS,Result.class);}catch(TimeoutException e){throw new AssertionError("Result timeout",e);}}
 void history(String id)throws Exception{WorkflowExecutionHistory h=client.fetchHistory(id);Files.writeString(output.resolve(id+".json"),h.toJson(true));}
 @Test void editedDefinitionExecutesWithoutWorkerRedeploy()throws Exception{ModelWorkflow w=start("golden-A",sample("A",1),"none");approve(w,"A");Result r=result(w);assertEquals("COMPLETED",r.state());assertEquals(List.of("admettre","validation","reserver","notifier"),r.completed());assertEquals(3,actions.effects.size());history("golden-A");new ObjectMapper().writeValue(output.resolve("actual-effects.json").toFile(),actions.journal);}
 @Test void humanRejectTakesAlternatePath(){ModelWorkflow w=start("reject-A",sample("A",1),"none");w.complete(new Outcome("no","A","validation","gestionnaire",false));assertEquals("REJECTED",result(w).state());assertFalse(actions.effects.keySet().stream().anyMatch(k->k.endsWith("reserver")));}
 @Test void timersEscalateUsingOfficialVirtualTime(){ModelWorkflow w=start("timeout-A",sample("A",1),"none");env.sleep(Duration.ofHours(5));assertEquals("ESCALATED",result(w).state());}
 @Test void duplicateSignalsAndWrongRoleDoNotCreateSecondOutcome(){ModelWorkflow w=start("signals-A",sample("A",1),"none");w.complete(new Outcome("x","B","validation","gestionnaire",true));w.complete(new Outcome("y","A","validation","lecteur",true));approve(w,"A");approve(w,"A");Result r=result(w);assertEquals("COMPLETED",r.state());assertTrue(r.rejected().containsAll(List.of("organisation","role")));assertEquals(1,r.completed().stream().filter(x->x.equals("validation")).count());}
 @Test void retryAfterCommittedEffectRequiresIdempotentAdapter(){ModelWorkflow w=start("lost-ack-A",sample("A",1),"lost-ack");approve(w,"A");assertEquals("COMPLETED",result(w).state());assertEquals(2,actions.attempts.get("A/lost-ack-A/admettre").get());assertEquals(1,actions.effects.keySet().stream().filter(k->k.endsWith("admettre")).count());}
 @Test void negativeControlTemporalAloneDoesNotMakeExternalSideEffectsExactlyOnce(){ModelWorkflow w=start("unsafe-A",sample("A",1),"non-idempotent");approve(w,"A");assertEquals("COMPLETED",result(w).state());assertEquals(2,actions.effects.keySet().stream().filter(k->k.contains("admettre")).count());}
 @Test void providerFailureCompensatesCommittedActions(){ModelWorkflow w=start("compensate-A",sample("A",1),"notify-always-fails");approve(w,"A");assertEquals("COMPENSATED",result(w).state());assertTrue(actions.effects.isEmpty());}
 @Test void oldInstancesRetainPublishedVersion()throws Exception{ModelWorkflow old=start("version-old-A",sample("A",1),"none"),fresh=start("version-new-A",sample("A",2),"none");approve(old,"A");approve(fresh,"A");assertEquals(1,result(old).definitionVersion());assertEquals(2,result(fresh).definitionVersion());assertTrue(result(old).completed().contains("notifier"));assertTrue(result(fresh).completed().contains("notifier_express"));history("version-old-A");history("version-new-A");}
 // Server/worker restart is exercised against the official persistent server by live-temporal.py and durable-restart.py.
 // The first in-memory replacement-worker fixture timed out; its result is retained in temporal-iteration-02.txt.
 @Test void waitingHistoryReplaysBeforeHumanAnswer()throws Exception{ModelWorkflow w=start("waiting-replay-A",sample("A",1),"none");WorkflowExecutionHistory h=client.fetchHistory("waiting-replay-A");WorkflowReplayer.replayWorkflowExecution(h,Interpreter.class);assertEquals(1,actions.effects.size());approve(w,"A");assertEquals("COMPLETED",result(w).state());assertEquals(3,actions.effects.size());history("waiting-replay-A");}
 @Test void recordedHistoryReplaysAndIncompatibleCodeIsRejected()throws Exception{ModelWorkflow w=start("replay-A",sample("A",1),"none");approve(w,"A");result(w);WorkflowExecutionHistory h=client.fetchHistory("replay-A");WorkflowReplayer.replayWorkflowExecution(h,Interpreter.class);assertThrows(Exception.class,()->WorkflowReplayer.replayWorkflowExecution(h,IncompatibleInterpreter.class));history("replay-A");}
 @Test void invalidGraphAndArbitraryServiceAreRejectedBeforeExecution(){Definition good=sample("A",1);validate(good);List<Step> changed=new ArrayList<>(good.steps());changed.set(0,new Step("admission","activity","run-arbitrary-code","validation",null,List.of(),0));assertThrows(IllegalArgumentException.class,()->validate(new Definition("A","bad",1,"admission",changed)));changed.set(0,new Step("admission","activity","admettre","admission",null,List.of(),0));assertThrows(IllegalArgumentException.class,()->validate(new Definition("A","bad",1,"admission",changed)));}
}
