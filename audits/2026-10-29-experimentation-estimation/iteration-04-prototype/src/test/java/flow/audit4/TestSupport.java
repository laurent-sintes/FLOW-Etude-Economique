package flow.audit4;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.TransactionDefinition;
import org.springframework.transaction.support.TransactionTemplate;
import javax.sql.DataSource;
public final class TestSupport {
 private static final HikariDataSource DS = create();
 private static HikariDataSource create() {
  HikariConfig c = new HikariConfig();
  String url=System.getenv("FLOW_AUDIT_JDBC_URL");
  if(url==null || !url.startsWith("jdbc:postgresql://127.0.0.1:")) throw new IllegalStateException("Isolated loopback PostgreSQL URL required");
  c.setJdbcUrl(url); c.setUsername(System.getenv("FLOW_AUDIT_JDBC_USER")); c.setPassword(System.getenv("FLOW_AUDIT_JDBC_PASSWORD"));
  c.setMaximumPoolSize(8); c.setMinimumIdle(0); c.setConnectionTimeout(10000); c.setPoolName("flow-audit4");
  return new HikariDataSource(c);
 }
 public static DataSource dataSource(){return DS;}
 public static JdbcTemplate jdbc(){return new JdbcTemplate(DS);}
 public static TransactionTemplate tx(){
  TransactionTemplate t=new TransactionTemplate(new DataSourceTransactionManager(DS));
  t.setIsolationLevel(TransactionDefinition.ISOLATION_READ_COMMITTED); t.setTimeout(30); return t;
 }
 private TestSupport(){}
}
