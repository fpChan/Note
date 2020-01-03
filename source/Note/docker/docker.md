# Docker 基础

### Docker 镜像  : image

Docker镜像是一个特殊的文件系统，它提供容器运行时所需的程序、库、资源、配置等文件，还包含了一些为运行时准备的一些配置参数（如匿名卷、环境变量、用户等）。镜像中不包含任何动态数据，其内容在构建之后也不会被改变，Docker引擎基于Docker镜像、提供运行时所需的配置参数就可以运行一个Docker容器。Docker镜像是一个虚拟的概念，设计时采用了分层存储的架构，由多层文件系统（如基础镜像）联合组成。

镜像构建时，会一层层构建，前一层是后一层的基础。每一层构建完就不会再发生改变，后一层上的任何改变只发生在自己这一层。比如，删除前一层文件的操作，实际不是真的删除前一层的文件，而是仅在当前层标记为该文件已删除。在最终容器运行的时候，虽然不会看到这个文件，但是实际上该文件会一直跟随镜像。因此，在构建镜像的时候，需要额外小心，每一层尽量只包含该层需要添加的东西，任何额外的东西应该在该层构建结束前清理掉。

分层存储的特征还使得镜像的复用、定制变的更为容易。甚至可以用之前构建好的镜像作为基础层，然后进一步添加新的层，以定制自己所需的内容，构建新的镜像。

容器运行时，会在镜像文件系统层上方再添加一个读写层，容器运行时在容器读写层进行文件读写操作，当容器停止时，docker引擎会删除容器读写层。

查看一个镜像的层次结构，可通过`docker history <image-id>`查看：



### 容器 : container

容器是镜像运行时的实体(镜像实例化)。容器可以被创建、启动、停止、删除、暂停等。

容器的实质是进程，但与直接在宿主执行的进程不同，容器进程运行于自己的独立的命名空间。因此容器可以拥有自己的 `root`文件系统、自己的网络配置、自己的进程空间，甚至自己的用户 ID 空间。

每一个容器运行时，是以镜像为基础层，在其上创建一个当前容器的存储层。容器存储层的生存周期和容器一样，因此，容器不应该向其存储层内写入任何数据，容器存储层要保持无状态化。所有的文件写入操作，都应该使用数据卷(Volume)、或者绑定宿主目录，在这些位置的读写会跳过容器存储层，直接对宿主（或网络存储）发生读写，其性能和稳定性更高。

### 常用命令

```dockerfile
# 显示本机镜像
docker images
docker image ls
# 编译镜像
docker build -t cfp/node
# 拉取镜像
docekr pull cfp/node-1:latest
# 推送镜像
docekr push cfp/node-1:latest
# 删除本地镜像
docker rmi cfp/node-1:latest
# 镜像tag
docker tag cfp/node-1:latest  cfp/node-1:v1.0
# 显示本地容器
docker ps -a
# 删除本地容器
docker rm full0
# 进入容器
docker exec -it full0 /bin/sh
# 进入容器
docker attach full0
# 启动、停止、重启容器
docker start/stop/restart
# 查看容器log
docker logs -f full0
# 启动容器
docker run cfp/node ls /go/src/github.com/cosmos/launch
# 使用容器生成镜像
docker commit -a "author" -m "message" full0 image:new
```

- docker exec 与 attache的区别
  - `docker exec -it`分配伪终端和stdin，跟正常的console一样执行命令
  - `docker attach` attach到一个已经运行的容器的stdin，然后进行命令执行。但是，**如果从这个stdin中exit(如ctl+c)，会导致容器的停止**
- docker commit 生成镜像
  - 将容器的存储层保存下来成为镜像的一层。就是在原有镜像的基础上，再叠加上容器的存储层，并构成新的镜像。以后我们运行这个新镜像的时候，就会拥有原有容器最后的文件变化。
  - `docker commit`生成镜像时黑箱操作，除了制作镜像的人知道执行过什么命令、怎么生成的镜像，别人根本无从得知。难用且不易维护。
  - `docker commit`生成镜像易包含其他无用修改，使镜像臃肿
  - **通常不建议使用此方式构建镜像，推荐使用Dockerfile**
  - 可用于特殊场景，如被入侵后保存现场等
  
  



