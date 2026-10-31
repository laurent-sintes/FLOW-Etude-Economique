package flow.trial;
import static flow.trial.ModelRuntime.*;
import com.fasterxml.jackson.databind.*;
import com.sun.net.httpserver.*;
import io.temporal.client.*;
import io.temporal.serviceclient.*;
import io.temporal.worker.*;
import io.temporal.api.enums.v1.WorkflowIdReusePolicy;
import org.springframework.context.annotation.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/** Local fixture identities are simulated; this server is not an SSO or production security implementation. */
public class TrialPortal {
 static final ObjectMapper JSON=new ObjectMapper();
 static final Path ROOT=Path.of(System.getProperty("trial.root","tmp/targeted-runtime/portal")).toAbsolutePath();
 static final Path EVIDENCE=Path.of(System.getProperty("trial.evidence","audits/2026-10-31-essais-temporal-mining/results/live")).toAbsolutePath();
 static final class DurableActions extends Actions {
  DurableActions(){try{if(Files.exists(ROOT.resolve("effects.json"))){Map<String,Object> s=JSON.readValue(ROOT.resolve("effects.json").toFile(),Map.class);((Map<String,String>)s.get("effects")).forEach(effects::put);((Map<String,Number>)s.get("attempts")).forEach((k,v)->attempts.put(k,new AtomicInteger(v.intValue())));}}catch(Exception e){throw new RuntimeException(e);}}
  synchronized void save(){try{Map<String,Integer> n=new HashMap<>();attempts.forEach((k,v)->n.put(k,v.get()));Files.writeString(ROOT.resolve("effects.json"),JSON.writeValueAsString(Map.of("effects",effects,"attempts",n)));}catch(Exception e){throw new RuntimeException(e);}}
  @Override public synchronized String apply(String o,String c,String a,String f){try{return super.apply(o,c,a,f);}finally{save();}}
  @Override public synchronized void compensate(String o,String c,String a){try{super.compensate(o,c,a);}finally{save();}}
 }
 @Configuration static class Wiring {@Bean WorkflowServiceStubs service(){return WorkflowServiceStubs.newServiceStubs(WorkflowServiceStubsOptions.newBuilder().setTarget("127.0.0.1:18973").setRpcTimeout(Duration.ofSeconds(5)).build());}@Bean WorkflowClient client(WorkflowServiceStubs s){return WorkflowClient.newInstance(s);}@Bean DurableActions actions(){return new DurableActions();}}
 static WorkflowClient client;static WorkerFactory factory;static DurableActions actions;static final Map<String,Definition> definitions=new ConcurrentHashMap<>();static final Map<String,String> answerHashes=new ConcurrentHashMap<>();
 static synchronized void startWorker(){factory=WorkerFactory.newInstance(client);Worker w=factory.newWorker("live-trial",WorkerOptions.newBuilder().setStickyQueueScheduleToStartTimeout(Duration.ofSeconds(1)).build());w.registerWorkflowImplementationTypes(Interpreter.class);w.registerActivitiesImplementations(actions);factory.start();}
 static synchronized void restart(){factory.shutdownNow();factory.awaitTermination(5,TimeUnit.SECONDS);startWorker();}
 static String principal(HttpExchange x){return Optional.ofNullable(x.getRequestHeaders().getFirst("X-Trial-User")).orElse("lecteur-A");}
 static String org(String principal){return principal.endsWith("-B")?"B":"A";}
 static String role(String principal){return principal.split("-")[0];}
 static String workflowId(String org,String id){if(id==null||!id.matches("[A-Za-z0-9_-]{1,70}"))throw new IllegalArgumentException("identifiant dossier");return org+"-"+id;}
 static Map<String,String> params(String q){Map<String,String> r=new HashMap<>();if(q!=null)for(String p:q.split("&")){String[] v=p.split("=",2);r.put(URLDecoder.decode(v[0],StandardCharsets.UTF_8),v.length>1?URLDecoder.decode(v[1],StandardCharsets.UTF_8):"");}return r;}
 static void reply(HttpExchange x,int code,Object value)throws Exception{byte[] bytes=JSON.writeValueAsBytes(value);x.getResponseHeaders().set("Content-Type","application/json; charset=utf-8");x.getResponseHeaders().set("Cache-Control","no-store");x.sendResponseHeaders(code,bytes.length);x.getResponseBody().write(bytes);x.close();}
 static String defkey(String org,int version){return org+"/"+version;}
 static synchronized Definition publish(String org,JsonNode b)throws Exception{
  int latest=definitions.values().stream().filter(d->d.organisation().equals(org)).mapToInt(Definition::version).max().orElse(0);if(b.path("expectedVersion").asInt()!=latest)throw new IllegalStateException("version obsolete");
  int version=latest+1;Definition d=sample(org,b.path("express").asBoolean()?2:1);List<Step> steps=new ArrayList<>(d.steps());
  if(b.path("control").asBoolean()){Step choice=steps.get(2);steps.set(2,new Step(choice.id(),choice.type(),null,"controle",choice.otherwise(),List.of(),0));steps.add(new Step("controle","activity","verifier_capacite","preparer",null,List.of(),0));}
  d=new Definition(org,b.path("name").asText("Réception"),version,d.start(),steps);validate(d);definitions.put(defkey(org,version),d);JSON.writeValue(ROOT.resolve("models.json").toFile(),definitions);return d;
 }
 static void handle(HttpExchange x){try{
  String path=x.getRequestURI().getPath(),principal=principal(x),organisation=org(principal);Map<String,String> q=params(x.getRequestURI().getQuery());
  if(path.equals("/")){byte[] html=TrialPortal.class.getResourceAsStream("/studio.html").readAllBytes();x.getResponseHeaders().set("Content-Type","text/html; charset=utf-8");x.sendResponseHeaders(200,html.length);x.getResponseBody().write(html);x.close();return;}
  if(path.equals("/health")){reply(x,200,Map.of("status","up","runtime","Temporal official dev server + SQLite","identities","synthetic"));return;}
  JsonNode b=x.getRequestMethod().equals("POST")?JSON.readTree(x.getRequestBody()):JSON.createObjectNode();
  switch(path){
   case "/models"->{if(x.getRequestMethod().equals("GET")){reply(x,200,definitions.values().stream().filter(d->d.organisation().equals(organisation)).sorted(Comparator.comparingInt(Definition::version)).toList());}else{if(!role(principal).equals("designer")){reply(x,403,Map.of("error","role"));return;}Definition d=publish(organisation,b);reply(x,201,d);}}
   case "/cases"->{String id=x.getRequestMethod().equals("POST")?b.path("caseId").asText():q.get("caseId"),wid=workflowId(organisation,id);if(x.getRequestMethod().equals("POST")){if(!Set.of("designer","gestionnaire").contains(role(principal))){reply(x,403,Map.of("error","role"));return;}Definition d=definitions.get(defkey(organisation,b.path("version").asInt()));if(d==null){reply(x,404,Map.of("error","version"));return;}ModelWorkflow w=client.newWorkflowStub(ModelWorkflow.class,WorkflowOptions.newBuilder().setWorkflowId(wid).setTaskQueue("live-trial").setWorkflowIdReusePolicy(WorkflowIdReusePolicy.WORKFLOW_ID_REUSE_POLICY_REJECT_DUPLICATE).build());WorkflowClient.start(w::run,d,new CaseInput(organisation,wid,b.path("failureMode").asText("none")));reply(x,202,Map.of("workflowId",wid,"version",d.version()));}else{ModelWorkflow w=client.newWorkflowStub(ModelWorkflow.class,wid);reply(x,200,w.state());}}
   case "/outcomes"->{if(!role(principal).equals("gestionnaire")){reply(x,403,Map.of("error","role"));return;}String wid=workflowId(organisation,b.path("caseId").asText()),event=b.path("eventId").asText(),digest=b.toString(),key=wid+"/"+event;String prior=answerHashes.putIfAbsent(key,digest);if(prior!=null){reply(x,prior.equals(digest)?200:409,Map.of("duplicate",true));return;}ModelWorkflow w=client.newWorkflowStub(ModelWorkflow.class,wid);if(!w.state().state().equals("WAITING")){answerHashes.remove(key);reply(x,409,Map.of("error","task not waiting"));return;}w.complete(new Outcome(event,organisation,"validation","gestionnaire",b.path("approved").asBoolean()));reply(x,202,Map.of("accepted",true));}
   case "/history"->{String wid=workflowId(organisation,q.get("caseId"));String history=client.fetchHistory(wid).toJson(true);Files.writeString(EVIDENCE.resolve(wid+".json"),history);reply(x,200,JSON.readTree(history));}
   case "/effects"->{reply(x,200,Map.of("effects",actions.effects.entrySet().stream().filter(e->e.getKey().startsWith(organisation+"/")).toList(),"attempts",actions.attempts.entrySet().stream().filter(e->e.getKey().startsWith(organisation+"/")).collect(java.util.stream.Collectors.toMap(Map.Entry::getKey,e->e.getValue().get()))));}
   case "/test/restart-worker"->{restart();reply(x,200,Map.of("restarted",true));}
   default->reply(x,404,Map.of("error","missing"));
  }
 }catch(WorkflowExecutionAlreadyStarted e){try{reply(x,409,Map.of("error","case already exists"));}catch(Exception ignored){}}catch(WorkflowNotFoundException e){try{reply(x,404,Map.of("error","case"));}catch(Exception ignored){}}catch(IllegalArgumentException e){try{reply(x,400,Map.of("error",e.getMessage()));}catch(Exception ignored){}}catch(IllegalStateException e){try{reply(x,409,Map.of("error",e.getMessage()));}catch(Exception ignored){}}catch(Exception e){try{reply(x,503,Map.of("error",e.getClass().getSimpleName()));}catch(Exception ignored){}}
 }
 public static void main(String[] args)throws Exception{Files.createDirectories(ROOT);Files.createDirectories(EVIDENCE);if(Files.exists(ROOT.resolve("models.json"))){JsonNode stored=JSON.readTree(ROOT.resolve("models.json").toFile());stored.fields().forEachRemaining(e->{try{definitions.put(e.getKey(),JSON.treeToValue(e.getValue(),Definition.class));}catch(Exception ex){throw new RuntimeException(ex);}});}AnnotationConfigApplicationContext ctx=new AnnotationConfigApplicationContext(Wiring.class);client=ctx.getBean(WorkflowClient.class);actions=ctx.getBean(DurableActions.class);startWorker();HttpServer server=HttpServer.create(new InetSocketAddress("127.0.0.1",18980),0);server.createContext("/",TrialPortal::handle);server.setExecutor(Executors.newVirtualThreadPerTaskExecutor());server.start();Runtime.getRuntime().addShutdownHook(new Thread(()->{server.stop(0);factory.shutdownNow();ctx.close();}));System.out.println("TRIAL_PORTAL_READY http://127.0.0.1:18980");}
}
