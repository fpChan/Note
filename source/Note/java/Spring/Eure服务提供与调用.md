# Eureka服务提供与调用

### 1.Maven依赖

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>Dalston.SR1</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-eureka</artifactId>
</dependency>
```

 

### 2.配置

Spring Cloud主要配置，见http://cloud.spring.io/spring-cloud-static/Dalston.SR1/#_appendix_compendium_of_configuration_properties

```yaml
## Eureka注册中心地址
eureka.client.serviceUrl.defaultZone=http://127.0.0.1:10000/eureka/
## 实例租期过期时间
eureka.instance.lease-expiration-duration-in-seconds=90
## 实例续约租期时间间隔
eureka.instance.lease-renewal-interval-in-seconds=30
## 使用ip地址对外提供服务
eureka.instance.preferIpAddress=true
```



### 3.注解启用

```java
@SpringBootApplication
@EnableEurekaClient
public class App {
     
    public static void main(String[] args) throws Exception {
        SpringApplication.run(App.class, args);
    }
     
}
```

 

### 4.服务的提供与调用

#### 4.1 服务提供者

##### 4.1.1 配置

```
## 该属性将作为Eureka注册的serviceId``spring.application.name=metal-nanapi
```

 

##### 4.1.2 提供REST服务

```java
@RestController
@ResponseBody
public class NanapiController {
  
    @RequestMapping(value = "/api/v1/{ADAPTER}", method = RequestMethod.POST)
    public ApiResult api(@PathVariable("ADAPTER") String ADAPTER, @RequestBody Map<String, String> params) {
        if (params == null) {
            return ApiResult.fail(ApiResult.PARAM_ERROR, "param can't be null");
        }
 
        try {
            String result = request(ADAPTER, params);
            if (result != null) {
                return ApiResult.success(result);
            } else {
                return ApiResult.fail(ApiResult.EXCEPTION, "request result is null");
            }
        } catch (Exception e) {
            logger.error("/api/v1/" + ADAPTER, e);
            return ApiResult.fail(ApiResult.EXCEPTION, e.getMessage());
        }
    }
}
```

 

#### 4.2 服务调用者

使用声明式REST客户端Feign

##### 4.2.1 Maven依赖

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-feign</artifactId>
</dependency>
```

 

##### 4.2.2 配置

```yaml

## 断路器hystrix超时时间
hystrix.command.default.execution.isolation.thread.timeoutInMilliseconds=30000
## 客户端负载均衡器Ribbon超时时间
ribbon.ReadTimeout=30000
ribbon.ConnectTimeout=30000
```

 

##### 4.2.3 编写Feign接口

```java
@FeignClient("metal-nanapi")
public interface NanapiClient {
    @RequestMapping(value = "/api/v1/{ADAPTER}", method = RequestMethod.POST)
    public ApiResult request(@PathVariable("ADAPTER") String ADAPTER, @RequestBody Map<String, String> params);
 
}
  
@FeignClient("common-components")
public interface BafangComponentClient {
    @RequestMapping(value = "/sms/send/template", method = RequestMethod.POST)
    public ApiResult smsSendByTemplate(@RequestParam Map<String, String> params);
  
}
```

说明：

- a. @FeignClient注解表明该接口是一个Feign客户端，运行时Spring会自动生成实现类Bean

- b. @FeignClient注解的值是服务的serviceId

- c. 以声明REST接口的形式表示需要调用的接口

 

##### 4.2.4 注解启用

```java
@SpringBootApplication
@EnableEurekaClient
@EnableFeignClients(clients={NanapiClient.class, BafangComponentClient.class})
public class App {
     
    public static void main(String[] args) throws Exception {
        SpringApplication.run(App.class, args);
    }
     
}
```

说明：如果所有Feign的client都在同一项目中，@EnableFeignClients可以不设置属性；否则（例如使用starter的情况）。

\* 如果有更好的方式可以简化设置，欢迎指正。

 

##### 4.2.5 FeignClient的使用

```java
@Component
public class TradeRestApi {
     
    @Autowired
    private static NanapiClient client;
  
    private static String request(String ADAPTER, BaseParams params) throws Exception {
        Map<String, String> map = params.toMap();
        ApiResult apiResult = client.request(ADAPTER, map);
  
        String result = null;
        if (apiResult.getStatus() == ApiResult.SUCCESS) {
            result = apiResult.getResult() == null ? null : apiResult.getResult().toString();
        }
        return null;
    }
}
```

