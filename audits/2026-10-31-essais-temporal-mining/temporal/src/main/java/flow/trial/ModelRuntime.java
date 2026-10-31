package flow.trial;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.temporal.activity.*;
import io.temporal.common.RetryOptions;
import io.temporal.failure.ActivityFailure;
import io.temporal.workflow.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/** Bounded metadata interpreter, deliberately a trial, not a production BPMN implementation. */
public final class ModelRuntime {
 public record Step(String id,String type,String service,String next,String otherwise,List<String> services,int timeoutHours) {}
 public record Definition(String organisation,String name,int version,String start,List<Step> steps) {}
 public record CaseInput(String organisation,String caseId,String failureMode) {}
 public record Outcome(String eventId,String organisation,String task,String role,boolean approved) {}
 public record Result(String state,int definitionVersion,List<String> completed,List<String> rejected) {}
 public static final Set<String> SERVICES=Set.of("admettre","reserver","notifier","notifier_express","expedier","verifier_capacite");
 public static void validate(Definition d){
  if(d.organisation()==null||d.organisation().isBlank()||d.version()<1||d.steps()==null||d.steps().size()>30)throw new IllegalArgumentException("definition envelope");
  Map<String,Step> idx=new LinkedHashMap<>();
  for(Step s:d.steps()){
   if(s.id()==null||idx.put(s.id(),s)!=null)throw new IllegalArgumentException("duplicate step");
   if(!Set.of("activity","human","choice","parallel","end","cancel").contains(s.type()))throw new IllegalArgumentException("unsupported type");
   if(s.type().equals("activity")&&!SERVICES.contains(s.service()))throw new IllegalArgumentException("service not in catalogue");
   if(s.type().equals("parallel")&&(s.services()==null||s.services().isEmpty()||s.services().size()>4||!SERVICES.containsAll(s.services())))throw new IllegalArgumentException("parallel catalogue");
   if(s.type().equals("human")&&(s.timeoutHours()<1||s.timeoutHours()>168))throw new IllegalArgumentException("human timeout");
  }
  if(!idx.containsKey(d.start()))throw new IllegalArgumentException("start");
  Set<String> visited=new HashSet<>(),active=new HashSet<>();walk(d.start(),idx,visited,active);
  if(visited.size()!=idx.size())throw new IllegalArgumentException("unreachable step");
 }
 private static void walk(String id,Map<String,Step> idx,Set<String> seen,Set<String> active){
  if(!idx.containsKey(id))throw new IllegalArgumentException("dangling edge");
  if(!active.add(id))throw new IllegalArgumentException("unbounded cycle");
  if(seen.add(id)){
   Step s=idx.get(id);
   if(!Set.of("end","cancel").contains(s.type())){walk(s.next(),idx,seen,active);if(s.type().equals("choice"))walk(s.otherwise(),idx,seen,active);}
  }
  active.remove(id);
 }
 public static Definition sample(String org,int version){return new Definition(org,"Réception et allocation",version,"admission",List.of(
  new Step("admission","activity","admettre","validation",null,List.of(),0),new Step("validation","human",null,"choix",null,List.of(),4),
  new Step("choix","choice",null,"preparer","refus",List.of(),0),new Step("preparer","parallel",null,"fin",null,List.of("reserver",version==1?"notifier":"notifier_express"),0),
  new Step("refus","cancel",null,null,null,List.of(),0),new Step("fin","end",null,null,null,List.of(),0)));}
 @WorkflowInterface public interface ModelWorkflow {
  @WorkflowMethod Result run(Definition definition,CaseInput input);
  @SignalMethod void complete(Outcome outcome);
  @QueryMethod Result state();
 }
 @ActivityInterface public interface BusinessActions {
  @ActivityMethod String apply(String organisation,String caseId,String action,String failureMode);
  @ActivityMethod void compensate(String organisation,String caseId,String action);
 }
 public static class Actions implements BusinessActions {
  public final ConcurrentHashMap<String,String> effects=new ConcurrentHashMap<>();
  public final ConcurrentHashMap<String,AtomicInteger> attempts=new ConcurrentHashMap<>();
  public final List<Map<String,Object>> journal=Collections.synchronizedList(new ArrayList<>());
  private String key(String o,String c,String a){return o+"/"+c+"/"+a;}
  public String apply(String org,String caseId,String action,String mode){
   String key=key(org,caseId,action);int n=attempts.computeIfAbsent(key,k->new AtomicInteger()).incrementAndGet();
   if("notify-always-fails".equals(mode)&&action.startsWith("notifier"))throw new IllegalStateException("synthetic provider unavailable");
   boolean unsafe="non-idempotent".equals(mode);String effective=unsafe?key+"/attempt-"+n:key;
   effects.computeIfAbsent(effective,k->{journal.add(Map.of("organisation",org,"caseId",caseId,"activity",action,"effectKey",effective,"observedAt",System.currentTimeMillis()));return k;});
   if(("lost-ack".equals(mode)||unsafe)&&action.equals("admettre")&&n==1)throw new IllegalStateException("synthetic response lost after commit");
   return key;
  }
  public void compensate(String org,String caseId,String action){effects.remove(key(org,caseId,action));journal.add(Map.of("organisation",org,"caseId",caseId,"activity","annuler_"+action,"observedAt",System.currentTimeMillis()));}
 }
 public static class Interpreter implements ModelWorkflow {
  private Definition def;private CaseInput input;private String state="NEW",pending;private boolean approved;
  private final List<Outcome> earlyOutcomes=new ArrayList<>();
  private final List<String> done=new ArrayList<>(),rejected=new ArrayList<>();private final Set<String> received=new HashSet<>();private final Map<String,Outcome> answers=new HashMap<>();
  private final BusinessActions actions=Workflow.newActivityStub(BusinessActions.class,ActivityOptions.newBuilder().setStartToCloseTimeout(Duration.ofSeconds(10)).setRetryOptions(RetryOptions.newBuilder().setInitialInterval(Duration.ofMillis(10)).setMaximumInterval(Duration.ofMillis(50)).setMaximumAttempts(3).build()).build());
  public Result run(Definition d,CaseInput c){
   validate(d);def=d;input=c;if(!d.organisation().equals(c.organisation()))throw new IllegalArgumentException("organisation mismatch");
   Map<String,Step> steps=new HashMap<>();for(Step s:d.steps())steps.put(s.id(),s);String next=d.start();state="RUNNING";
   List<String> compensable=new ArrayList<>();
   try{
    for(int guard=0;guard<30;guard++){
     Step s=steps.get(next);switch(s.type()){
      case "activity"->{actions.apply(c.organisation(),c.caseId(),s.service(),c.failureMode());done.add(s.service());compensable.add(s.service());next=s.next();}
      case "human"->{pending=s.id();state="WAITING";for(Outcome early:new ArrayList<>(earlyOutcomes))acceptForPending(early);earlyOutcomes.clear();boolean ok=Workflow.await(Duration.ofHours(s.timeoutHours()),()->answers.containsKey(s.id()));if(!ok){state="ESCALATED";return state();}approved=answers.get(s.id()).approved();done.add("validation");pending=null;state="RUNNING";next=s.next();}
      case "choice"->next=approved?s.next():s.otherwise();
      case "parallel"->{List<Promise<String>> calls=new ArrayList<>();for(String service:s.services()){calls.add(Async.function(actions::apply,c.organisation(),c.caseId(),service,c.failureMode()));compensable.add(service);}Promise.allOf(calls).get();done.addAll(s.services());next=s.next();}
      case "cancel"->{state="REJECTED";return state();}
      case "end"->{state="COMPLETED";return state();}
      default->throw new IllegalStateException("unreachable type");
     }
    }
    throw new IllegalStateException("guard");
   }catch(ActivityFailure failure){for(String service:compensable.reversed())actions.compensate(c.organisation(),c.caseId(),service);state="COMPENSATED";return state();}
  }
  public void complete(Outcome o){if(def==null||pending==null){earlyOutcomes.add(o);return;}acceptForPending(o);}
  private void acceptForPending(Outcome o){
   if(def==null||!def.organisation().equals(o.organisation())){rejected.add("organisation");return;}
   if(!"gestionnaire".equals(o.role())){rejected.add("role");return;}
   if(!Objects.equals(pending,o.task())){rejected.add("task");return;}
   if(!received.add(o.eventId()))return;
   if(answers.containsKey(o.task()))return;answers.put(o.task(),o);
  }
  public Result state(){return new Result(state,def==null?0:def.version(),new ArrayList<>(done),new ArrayList<>(rejected));}
 }
 public static final class IncompatibleInterpreter implements ModelWorkflow {
  public Result run(Definition d,CaseInput c){Workflow.sleep(Duration.ofSeconds(1));return new Result("WRONG",d.version(),List.of(),List.of());}
  public void complete(Outcome o){}public Result state(){return new Result("WRONG",0,List.of(),List.of());}
 }
}
