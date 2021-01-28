# Nginx

Nginx 的模块根据其功能基本上可以分为以下几种类型：

- event module: 搭建了独立于操作系统的事件处理机制的框架，及提供了各具体事件的处理。包括 ngx_events_module， ngx_event_core_module和ngx_epoll_module 等。Nginx 具体使用何种事件处理模块，这依赖于具体的操作系统和编译选项。

- phase handler: 此类型的模块也被直接称为 handler 模块。主要负责处理客户端请求并产生待响应内容，比如 ngx_http_static_module 模块，负责客户端的静态页面请求处理并将对应的磁盘文件准备为响应内容输出。

- output filter: 也称为 filter 模块，主要是负责对输出的内容进行处理，可以对输出进行修改。例如，可以实现对输出的所有 html 页面增加预定义的 footbar 一类的工作，或者对输出的图片的 URL 进行替换之类的工作。

- upstream: upstream 模块实现反向代理的功能，将真正的请求转发到后端服务器上，并从后端服务器上读取响应，发回客户端。upstream 模块是一种特殊的 handler，只不过响应内容不是真正由自己产生的，而是从后端服务器上读取的。

- load-balancer: 负载均衡模块，实现特定的算法，在众多的后端服务器中，选择一个服务器出来作为某个请求的转发服务器。


example:
```
upstream getsvr {
    #server 13.231.34.83:1317;#请求rest地址
    server 192.168.13.125:26659;#请求rest地址
}

    server {
        listen 7777;
        location / {
            add_header Access-Control-Allow-Origin 'http://192.168.71.154:5200';#需要设置前端部署的地址
                add_header Access-Control-Allow-Methods 'POST, GET, OPTIONS';
                add_header Access-Control-Allow-Headers 'X-Requested-With,Content-Type,origin, content-type, accept, authorization,Action, Module, access-control-allow-origin,app-type,timeout,devid';
                add_header Access-Control-Allow-Credentials true;
                if ($request_method = 'OPTIONS') {
                        return 204;
                }
                proxy_pass http://getsvr;
        }
    }
```


Nginx 使用一个多进程模型来对外提供服务，其中一个 master 进程，多个 worker 进程。master 进程负责管理 Nginx 本身和其他 worker 进程。

所有实际上的业务处理逻辑都在 worker 进程。worker 进程中有一个函数，执行无限循环，不断处理收到的来自客户端的请求，并进行处理，直到整个 Nginx 服务被停止。

worker 进程中，ngx_worker_process_cycle()函数就是这个无限循环的处理函数。在这个函数中，一个请求的简单处理流程如下：

- 操作系统提供的机制（例如 epoll, kqueue 等）产生相关的事件。
- 接收和处理这些事件，如是接受到数据，则产生更高层的 request 对象。
- 处理 request 的 header 和 body。
- 产生响应，并发送回客户端。
- 完成 request 的处理。
- 重新初始化定时器及其他事件。

### 请求的处理流程
为了让大家更好的了解 Nginx 中请求处理过程，我们以 HTTP Request 为例，来做一下详细地说明。

从 Nginx 的内部来看，一个 HTTP Request 的处理过程涉及到以下几个阶段。

- 初始化 HTTP Request（读取来自客户端的数据，生成 HTTP Request 对象，该对象含有该请求所有的信息）。
- 处理请求头。
- 处理请求体。
- 如果有的话，调用与此请求（URL 或者 Location）关联的 handler。
- 依次调用各 phase handler 进行处理。

在这里，我们需要了解一下 phase handler 这个概念。phase 字面的意思，就是阶段。所以 phase handlers 也就好理解了，就是包含若干个处理阶段的一些 handler。

在每一个阶段，包含有若干个 handler，再处理到某个阶段的时候，依次调用该阶段的 handler 对 HTTP Request 进行处理。

通常情况下，一个 phase handler 对这个 request 进行处理，并产生一些输出。通常 phase handler 是与定义在配置文件中的某个 location 相关联的。

一个 phase handler 通常执行以下几项任务：

- 获取 location 配置。
- 产生适当的响应。
- 发送 response header。
- 发送 response body。

当 Nginx 读取到一个 HTTP Request 的 header 的时候，Nginx 首先查找与这个请求关联的虚拟主机的配置。如果找到了这个虚拟主机的配置，那么通常情况下，这个 HTTP Request 将会经过以下几个阶段的处理（phase handlers）：

- NGX_HTTP_POST_READ_PHASE: 读取请求内容阶段
- NGX_HTTP_SERVER_REWRITE_PHASE: Server 请求地址重写阶段
- NGX_HTTP_FIND_CONFIG_PHASE: 配置查找阶段:
- NGX_HTTP_REWRITE_PHASE: Location请求地址重写阶段
- NGX_HTTP_POST_REWRITE_PHASE: 请求地址重写提交阶段
- NGX_HTTP_PREACCESS_PHASE: 访问权限检查准备阶段
- NGX_HTTP_ACCESS_PHASE: 访问权限检查阶段
- NGX_HTTP_POST_ACCESS_PHASE: 访问权限检查提交阶段
- NGX_HTTP_TRY_FILES_PHASE: 配置项 try_files 处理阶段
- NGX_HTTP_CONTENT_PHASE: 内容产生阶段
- NGX_HTTP_LOG_PHASE: 日志模块处理阶段

在内容产生阶段，为了给一个 request 产生正确的响应，Nginx 必须把这个 request 交给一个合适的 content handler 去处理。如果这个 request 对应的 location 在配置文件中被明确指定了一个 content handler，那么Nginx 就可以通过对 location 的匹配，直接找到这个对应的 handler，并把这个 request 交给这个 content handler 去处理。这样的配置指令包括像，perl，flv，proxy_pass，mp4等。

如果一个 request 对应的 location 并没有直接有配置的 content handler，那么 Nginx 依次尝试:

- 如果一个 location 里面有配置 random_index on，那么随机选择一个文件，发送给客户端。
- 如果一个 location 里面有配置 index 指令，那么发送 index 指令指明的文件，给客户端。
- 如果一个 location 里面有配置 autoindex on，那么就发送请求地址对应的服务端路径下的文件列表给客户端。
- 如果这个 request 对应的 location 上有设置 gzip_static on，那么就查找是否有对应的.gz文件存在，有的话，就发送这个给客户端（客户端支持 gzip 的情况下）。
- 请求的 URI 如果对应一个静态文件，static module 就发送静态文件的内容到客户端。
内容产生阶段完成以后，生成的输出会被传递到 filter 模块去进行处理。filter 模块也是与 location 相关的。所有的 fiter 模块都被组织成一条链。输出会依次穿越所有的 filter，直到有一个 filter 模块的返回值表明已经处理完成。

这里列举几个常见的 filter 模块，例如：

- server-side includes。
- XSLT filtering。
- 图像缩放之类的。
- gzip 压缩。

在所有的 filter 中，有几个 filter 模块需要关注一下。按照调用的顺序依次说明如下：

- write: 写输出到客户端，实际上是写到连接对应的 socket 上。
- postpone: 这个 filter 是负责 subrequest 的，也就是子请求的。
- copy: 将一些需要复制的 buf(文件或者内存)重新复制一份然后交给剩余的 body filter 处理。

参考如下：  
[深入浅出Nginx](https://www.jianshu.com/p/5eab0f83e3b4)  
[Nginx入门指南](http://wiki.jikexueyuan.com/project/nginx/nginx-framework.html)  