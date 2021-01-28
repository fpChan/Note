
# Docker Compose
### Docker Compose 介绍
Docker Compose 是 Docker 官方编排（orchestration）项目之一，负责快速的部署分布式应用。

它允许用户通过一个Docker-compose.yml 模板文件（YAML 格式）来定义一组相关联的应用容器为一个项目（project）。

- 服务 (Service)：一个应用的容器，实际上可以包括若干运行相同镜像的容器实例。
- 项目 (Project)：由一组关联的应用容器组成的一个完整业务单元，在 Docker-compose.yml 文件中定义。
- Compose 的默认管理对象是项目，通过子命令对项目中的一组容器进行便捷地生命周期管理。
- Compose 项目由 Python 编写，实现上调用了 Docker 服务提供的 API 来对容器进行管理。

### 常用命令

大部分命令跟`docker`下的命令功能相同

#### up

尝试自动完成包括构建镜像，（重新）创建服务，启动服务，并关联服务相关容器

```
docker-compose -f localhost.yml up -d
```

- `-f`指定使用的 Compose 模板文件，默认为 `docker-compose.yml`，可以多次指定
- `-d`后台启动并运行所有的容器
- 默认网络为`bridge`，可通过`--x-network-driver DRIVER`设置
- 默认，如果服务容器已经存在，`docker-compose up`将会尝试停止容器，然后重新创建（保持使用 `volumes-from`挂载的卷），以保证新启动的服务匹配 `docker-compose.yml`文件的最新内容。
- 如果用户不希望容器被停止并重新创建，可以使用 `docker-compose up --no-recreate`。这样将只会启动处于停止状态的容器，而忽略已经运行的服务。
- 如果用户只想重新部署某个服务，可以使用 `docker-compose up --no-deps -d <SERVICE_NAME>`来重新创建服务并后台停止旧服务，启动新服务，并不会影响到其所依赖的服务。

#### down

停止 `up`命令所启动的容器，并移除网络

```
docker-compose -f localhost.yml down
```

#### stop

停止已经处于运行状态的容器，但不删除。通过 `docker-compose start`可以再次启动这些容器

```
docker-compose -f localhost.yml stop nginx
```

- 如果不指定服务名，即停止yml文件中的所有服务容器

#### start

启动已经存在的服务容器

```
docker-compose -f localhost.yml start nginx
```

- 如果不指定服务名，即启动yml文件中的所有服务容器



#### 其余常用命令

```shell
# 登录到nginx容器中
docker-compose exec nginx bash           

# 重新启动nginx容器
docker-compose restart nginx    

# 暂停nignx容器
docker-compose pause nginx                 

#  恢复ningx容器
docker-compose unpause nginx            

# 删除容器（删除前必须关闭容器）
docker-compose rm nginx                       

# 停止nignx容器
docker-compose stop nginx                    

# 启动nignx容器
docker-compose start nginx    

# 在php-fpm中不启动关联容器，并容器执行php -v 执行完成后删除容器
docker-compose run --no-deps --rm php-fpm php -v  

# 构建镜像 
docker-compose build nginx                             

# 不带缓存的构建。
docker-compose build --no-cache nginx   

# 验证（docker-compose.yml）文件配置，当配置正确时，不输出任何内容，当文件配置错误，输出错误信息。 
docker-compose config  -q       

# 查看nginx的日志 
docker-compose logs  nginx                     

# 查看nginx的实时日志
docker-compose logs -f nginx                   
 
# 以json的形式输出nginx的docker日志
docker-compose events --json nginx     
```

 





### docker-compose file

#### 分解案例

```yaml
##服务基于已经存在的镜像
services:
  web:
    image: hello-world


##服务基于dockerfile 
build: /path/to/build/dir
build: ./dir
build:
  context: ../
  dockerfile: path/of/Dockerfile

build: ./dir
image: webapp:tag


##command command命令可以覆盖容器启动后默认执行的命令
command: bundle exec thin -p 3000
command: [bundle, exec, thin, -p, 3000]

##container_name
## Compose 的容器名称格式是：<项目名称><服务名称><序号>
## 虽然可以自定义项目名称、服务名称，但是如果你想完全控制容器的命名，可以使用这个标签指定
container_name: app

##depends_on depends_on解决了容器的依赖、启动先后的问题
version: '2'
services:
  web:
    build: .
    depends_on:
      - db
      - redis
  redis:
    image: redis
  db:


##dns
dns: 8.8.8.8
dns:
  - 8.8.8.8
  - 9.9.9.9

dns_search: example.com
dns_search:
  - dc1.example.com
  - dc2.example.com

##tmfs 挂载临时目录到容器内部，与run的参数一样效果
tmpfs: /run
tmpfs:
  - /run
  - /tmp

##environment 设置镜像变量，它可以保存变量到镜像里，也就是说启动的容器也会包含这些变量设置
environment:
  RACK_ENV: development
  SHOW: 'true'
  SESSION_SECRET:
 
environment:
  - RACK_ENV=development
  - SHOW=true
  - SESSION_SECRET
 
##expose  用于指定暴露的端口，但是只是作为参考，端口映射的话还得ports标签
expose:
 - "3000"
 - "8000"

##external_links
# 在使用Docker的过程中，我们会有许多单独使用docker run启动的容器，为了使Compose能够连接这些不在docker-compose.yml中定义的容器，我们需要一个特殊的标签，就是external_links，它可以让Compose项目里面的容器连接到那些项目配置外部的容器（前提是外部容器中必须至少有一个容器是连接到与项目内的服务的同一个网络里面）
 
external_links:
 - redis_1
 - project_db_1:mysql
 - project_db_1:postgresql

##extra_hosts  添加主机名的标签，就是往容器内部/etc/hosts文件中添加一些记录
extra_hosts:
 - "somehost:162.242.195.82"
 - "otherhost:50.31.209.229"

##labels 向容器添加元数据，和Dockerfile的lable指令一个意思

labels:
  com.example.description: "Accounting webapp"
  com.example.department: "Finance"
  com.example.label-with-empty-value: ""
labels:
  - "com.example.description=Accounting webapp"
  - "com.example.department=Finance"
  - "com.example.label-with-empty-value"
 
##links
# 解决容器连接问题，与docker的–link一样的效果，会连接到其他服务中的容器,使用的别名将会自动在服务容器中的/etc/hosts里创建
links:
 - db
 - db:database
 - redis


##ports
# 用作端口映射
# 使用HOST:CONTAINER格式或者只是指定容器的端口，宿主机会随机映射端口
ports:
 - "3000"
 - "8000:8000"
 - "49100:22"
 - "127.0.0.1:8001:8001"
# 当使用HOST:CONTAINER格式来映射端口时，如果你使用的容器端口小于60你可能会得到错误得结果，因为YAML将会解析xx:yy这种数字格式为60进制。所以建议采用字符串格式

##security_opt
# 为每个容器覆盖默认的标签。简单说来就是管理全部服务的标签，比如设置全部服务的user标签值为USER
security_opt:
  - label:user:USER
  - label:role:ROLE

##volumes
# 挂载一个目录或者一个已经存在的数据卷容器，可以直接使用[HOST:CONTAINER]这样的格式，或者使用[HOST:CONTAINER:ro]这样的格式，或者对于容器来说，数据卷是只读的，这样可以有效保护宿主机的文件系统。
# compose的数据卷指定路径可以是相对路径，使用 . 或者 … 来指定性对目录
 
volumes:
  // 只是指定一个路径，Docker 会自动在创建一个数据卷（这个路径是容器内部的）。
  - /var/lib/mysql
 
  // 使用绝对路径挂载数据卷
  - /opt/data:/var/lib/mysql
 
  // 以 Compose 配置文件为中心的相对路径作为数据卷挂载到容器。
  - ./cache:/tmp/cache
 
  // 使用用户的相对路径（~/ 表示的目录是 /home/<用户目录>/ 或者 /root/）。
  - ~/configs:/etc/configs/:ro
 
  // 已经存在的命名的数据卷。
  - datavolume:/var/lib/mysql
 
# 如果你不使用宿主机的路径，你可以指定一个volume_driver。
volume_driver: mydriver

##volumes_from
# 从其它容器或者服务挂载数据卷，可选的参数是:ro或者:rw，前者表示容器只读，后者表示容器对数据卷是可读可写的，默认是可读可写的

volumes_from:
  - service_name
  - service_name:ro
  - container:container_name
  - container:container_name:rw

##network_mode
# 网络模式，与docker client的–net参数类似，只是相对多了一个service:[sevice name]的格式
network_mode: "bridge"
network_mode: "host"
network_mode: "none"
network_mode: "service:[service name]"
network_mode: "container:[container name/id]"
 
##networks 加入指定网络
services:
  some-service:
    networks:
     - some-network
     - other-network
```





### Compose file版本和兼容性

| **Compose file format** | **Docker Engine release** |
| ----------------------- | ------------------------- |
| 3.7                     | 18.06.0+                  |
| 3.6                     | 18.02.0+                  |
| 3.5                     | 17.12.0+                  |
| 3.4                     | 17.09.0+                  |
| 3.3                     | 17.06.0+                  |
| 3.2                     | 17.04.0+                  |
| 3.1                     | 1.13.1+                   |
| 3.0                     | 1.13.0+                   |
| 2.4                     | 17.12.0+                  |
| 2.3                     | 17.06.0+                  |
| 2.2                     | 1.13.0+                   |
| 2.1                     | 1.12.0+                   |
| 2.0                     | 1.10.0+                   |
| 1.0                     | 1.9.1.+                   |