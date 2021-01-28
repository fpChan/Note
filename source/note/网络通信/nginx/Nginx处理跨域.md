# nginx代理跨域

#### nginx反向代理接口跨域

跨域原理： 同源策略是浏览器的安全策略，不是HTTP协议的一部分。服务器端调用HTTP接口只是使用HTTP协议，不会执行JS脚本，不需要同源策略，也就不存在跨越问题。

实现思路：通过nginx配置一个代理服务器（域名与domain1相同，端口不同）做跳板机，反向代理访问domain2接口，并且可以顺便修改cookie中domain信息，方便当前域cookie写入，实现跨域登录。

nginx具体配置：
```
#proxy服务器
server {
    listen       81;
    server_name  www.domain1.com;

    location / {
        proxy_pass   http://www.domain2.com:8080;  #反向代理
        proxy_cookie_domain www.domain2.com www.domain1.com; #修改cookie里域名
        index  index.html index.htm;

        # 当用webpack-dev-server等中间件代理接口访问nignx时，此时无浏览器参与，故没有同源限制，下面的跨域配置可不启用
        add_header Access-Control-Allow-Origin http://www.domain1.com;  #当前端只跨域不带cookie时，可为*
        add_header Access-Control-Allow-Credentials true;
    }
}
```

### 配置
```
location / {  
  add_header Access-Control-Allow-Origin *;
  add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept";
  add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
} 
```
####  1. Access-Control-Allow-Origin
服务器默认是不被允许跨域的。给Nginx服务器配置Access-Control-Allow-Origin *后，表示服务器可以接受所有的请求源（Origin）,即接受所有跨域的请求。
#### 2. Access-Control-Allow-Headers 
是为了防止出现以下错误：
```
Request header field Content-Type is not allowed by Access-Control-Allow-Headers in preflight response.
```
这个错误表示当前请求Content-Type的值不被支持。其实是我们发起了"application/json"的类型请求导致的。

####  3. Access-Control-Allow-Methods 
是为了防止出现以下错误：
```
Content-Type is not allowed by Access-Control-Allow-Headers in preflight response.
```
发送"预检请求"时，需要用到方法 OPTIONS ,所以服务器需要允许该方法。

### 预检请求（preflight request）
> 跨域资源共享(CORS)标准新增了一组 HTTP 首部字段，允许服务器声明哪些源站有权限访问哪些资源。另外，规范要求，对那些可能对服务器数据产生副作用的HTTP 请求方法（特别是 GET 以外的 HTTP 请求，或者搭配某些 MIME 类型的 POST 请求），浏览器必须首先使用 OPTIONS 方法发起一个预检请求（preflight request），从而获知服务端是否允许该跨域请求。服务器确认允许之后，才发起实际的 HTTP 请求。在预检请求的返回中，服务器端也可以通知客户端，是否需要携带身份凭证（包括 Cookies 和 HTTP 认证相关数据）。

Content-Type不属于以下MIME类型的，都属于预检请求：
```
application/x-www-form-urlencoded
multipart/form-data
text/plain
```
所以 application/json的请求 会在正式通信之前，增加一次"预检"请求，这次"预检"请求会带上头部信息 Access-Control-Request-Headers: Content-Type