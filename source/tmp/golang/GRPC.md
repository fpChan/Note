# RPC 

RPC（Remote Procedure Call），即远程过程调用，是一个分布式系统间通信的必备技术。RPC 最核心要解决的问题就是在**分布式系统间，如何执行另外一个地址空间上的函数、方法**，就仿佛在本地调用一样。

rpc是远端过程调用，其调用协议通常包含传输协议和编码协议

### 传输（Transport）

TCP 协议是 RPC 的 基石，一般来说通信是建立在 TCP 协议之上的，而且 RPC 往往需要可靠的通信，因此不采用 UDP。
**RPC 传输的 message 也就是 TCP body 中的数据**，这个 message 也同样可以包含 header+body。body 也经常叫做 payload。
TCP 协议栈存在端口的概念，端口是进程获取数据的渠道。

### **I/O 模型（I/O Model）**

做一个高性能 /scalable 的 RPC，需要能够满足：

- 服务端尽可能多的处理并发请求
- 同时尽可能短的处理完毕。

Socket I/O 可以看做是二者之间的桥梁，如何更好地协调二者，去满足前面说的两点要求，有一些模式（pattern）是可以应用的。RPC 框架可选择的 I/O 模型严格意义上有 5 种，这里不讨论基于 信号驱动 的 I/O（Signal Driven I/O）。它们分别是：

- 传统的阻塞 I/O（Blocking I/O）
- 非阻塞 I/O（Non-blocking I/O）
- I/O 多路复用（I/O multiplexing）
- 异步 I/O（Asynchronous I/O）





### 参考如下：

[理解REST和RPC](https://www.cnblogs.com/houkai/p/9772111.html)



RPC 

Go语言的RPC框架有两个比较有特色的设计：

- 一个是RPC数据打包时可以通过插件实现自定义的编码和解码；
- 另一个是RPC建立在抽象的io.ReadWriteCloser接口之上的

