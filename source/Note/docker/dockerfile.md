# Docker file
### Docker file 分析
**Dockerfile**是一个文本文件，用于构建生成Docker镜像，其内**以一个镜像为基础**，在基础镜像之上通过一条条的 指令(Instruction)加工、定制，最终产出自己想要的镜像。每一条指令都基于前一层依赖的镜像层构建一层新的镜像层，因此每一条指令的内容，就是描述该层应当如何构建。

```dockerfile
FROM cfp/build as builder

# Set working directory for the build
WORKDIR $GOPATH/src/github.com/fpchan/cfp

# Add cfp source files
COPY . .

# build cfp
RUN make install
RUN make launchcmd

# FROM cfp/node
FROM cfp/build

# Set working directory for the build
WORKDIR $GOPATH/src/github.com/cosmos/launch

ARG LAUNCH_REPOSITORY=https://github.com/cfp/launch
ARG LAUNCH_BRANCH=dev
ARG SEED_NODE_NUM=1
ARG VAL_NODE_NUM=1
ARG FULL_NODE_NUM=1

RUN mkdir -p $GOPATH/src/github.com/cosmos \
    && cd $GOPATH/src/github.com/cosmos \
    && git clone $LAUNCH_REPOSITORY -b $LAUNCH_BRANCH

COPY --from=builder $GOPATH/bin $GOPATH/bin
COPY docker/launch/genfile.sh .
COPY docker/launch/start.sh .

EXPOSE 26656 26657 26658 26659 6060

# generate genesis file
RUN $GOPATH/src/github.com/cosmos/launch/genfile.sh  ${SEED_NODE_NUM} ${VAL_NODE_NUM} ${FULL_NODE_NUM}
ENTRYPOINT $GOPATH/src/github.com/cosmos/launch/start.sh
docker build \
--build-arg SEED_NODE_NUM=1 \
--build-arg VAL_NODE_NUM=4 \
--build-arg FULL_NODE_NUM=10 \
-f Dockerfile -t cfp/node-1:rr .
```

- `FROM`指定基础镜像
- COPY从构建上下文目录中 <源路径> 的文件/目录复制到新的一层的镜像内的<目标路径>位置
  - **构建上下文目录**是指`docker build`指定的目录，通常使用`.`即当前目录，操作文件不可以超出上下文目录
  - `COPY [--chown=<user>:<group>] <源路径>... <目标路径>`
  - `COPY [--chown=<user>:<group>] ["<源路径1>",... "<目标路径>"]`
- `ADD`与`COPY`基本一致，但如果<源路径>是URL或者压缩文件，`ADD`可以自动下载和解压
- `RUN`指定要执行的命令
  - *shell*  格式：`RUN <命令>`
  - *exec* 格式：`RUN ["可执行文件", "参数1", "参数2"]`
- `CMD`启动容器时执行的命令，格式同`RUN`
  - 在运行时可以替代，`docker run`中执行指定的指令或docker-compose中的command
  - 在指令格式上，一般推荐使用 `exec`格式，这类格式在解析时会被解析为 JSON 数组，因此一定要使用双引号 `"`，而不要使用单引号
- `ENTRYPOINT` 同 `CMD`含义相同，格式同`RUN`
  - 当同时执行`CMD`和`ENTRYPOINT`后，`CMD`不再是直接的运行命令，二是将其作为参数传给`ENTRYPOINT`，变成`<ENTRYPOINT> "<CMD>"`
  - `ENTRYPOINT`比`CMD`的优势：
    - 如果指定`CMD [ "curl", "-s", "https://ip.cn" ]`，执行`docker run {images}`会输出IP，如果想加入参数`-i`，则执行`docker run {images} -i`会报错
    - 如果指定`ENTRYPOINT [ "curl", "-s", "https://ip.cn" ]`，同样的执行`docker run {images} -i`则没问题，相当于执行`curl -s https://ip.cn -i`
- `ENV`环境变量
- `ARG`构建参数
- `EXPOSE`声明容器提供的服务端口
- `WORKDIR`工作目录
- `USER`指定当前用户

### Docker file 最佳实践

- 使用`.dockerignore`文件
- 使用多阶段构建
  - 多阶段构建，允许在一个Dockerfile中使用多个FROM指令，可直接将前置阶段、或其他镜像中的资源文件复制到当前构建阶段，并最终只产生最后一个镜像，大大减少了镜像大小及个数
- 避免安装不必要的包
- 一个容器只运行一个进程
- 镜像层数尽可能少
- 构建缓存
  - 如果你不想在构建过程中使用缓存，你可以在 `docker build`命令中使用 `--no-cache=true`选项
- 将多个 RUN 指令合并为一个
  - Dockerfile 中的每个指令都会创建一个新的镜像层。
  - 镜像层将被缓存和复用
  - 当 Dockerfile 的指令修改了，复制的文件变化了，或者构建镜像时指定的变量不同了，对应的镜像层缓存就会失效
  - 某一层的镜像缓存失效之后，它之后的镜像层缓存都会失效
  - 镜像层是不可变的，如果我们再某一层中添加一个文件，然后在下一层中删除它，则镜像中依然会包含该文件(只是这个文件在 Docker 容器中不可见了)
- 基础镜像的标签不要用 latest
  - 当镜像更新时，latest 标签会指向不同的镜像，这时构建镜像有可能失败
- 每个 RUN 指令后删除多余文件
- 选择合适的基础镜像(alpine 版本最好)
  - alpine 是一个极小化的 Linux 发行版，只有 4MB，这让它非常适合作为基础镜像
- COPY 与 ADD 优先使用前者
  - COPY指令非常简单，仅用于将文件拷贝到镜像中。ADD相对来讲复杂，可以用于下载远程文件以及解压压缩包
- 合理调整 COPY 与 RUN 的顺序
  - 应该**把变化最少的部分放在 Dockerfile 的前面**，这样可以充分利用镜像缓存。