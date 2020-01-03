# websocket

建立在 TCP 协议之上

WebSocket协议建立在http协议的基础之上，因此二者有很多的类似之处。事实上，在使用websocket协议时，浏览器与服务端最开始建立的还是http连接，之后再将协议从http转换成websocket，协议转换的过程称之为握手(handshake)，表示服务端与客户端都同意建立websocket协议。

#### 请求
```
GET ws://server.example.com/ws HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Protocol: chat, superchat
Sec-WebSocket-Version: 13
Origin: http://example.com
```
`Upgrade`字段表示将通信协议从`HTTP/1.1`转向该字段指定的协议。  
`Connection`字段表示浏览器通知服务器，如果可以的话，就升级到`WebSocket`协议。  
`Origin`字段用于提供请求发出的域名，供服务器验证是否许可的范围内（服务器也可以不验证）。  
`Sec-WebSocket-Key`则是用于握手协议的密钥，是Base64 编码的16字节随机字符串。

注意GET的路径是以ws开头，这是因为WebSocket是一种全新的协议，不属于http无状态协议，协议名为”ws"，与http协议使用相同的80端口，类似的，"wss"和https协议使用相同的443端口。

#### 响应
```
HTTP/1.1 101 Switching Protocols
Connection: Upgrade
Upgrade: websocket
Sec-WebSocket-Accept: fFBooB7FAkLlXgRSz0BT3v4hq5s=
Sec-WebSocket-Origin: null
Sec-WebSocket-Location: ws://example.com/
```
服务器同样用`Connection`字段通知浏览器，需要改变协议。  
`Sec-WebSocket-Accept`字段是服务器在浏览器提供的`Sec-WebSocket-Key`字符串后面，添加 RFC6456 标准规定的“258EAFA5-E914-47DA-95CA-C5AB0DC85B11”字符串，然后再取 SHA-1 的哈希值。浏览器将对这个值进行验证，以证明确实是目标服务器回应了 WebSocket 请求。  
`Sec-WebSocket-Location`字段表示进行通信的`WebSocket` 网址。

#### 格式

```
  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-------+-+-------------+-------------------------------+
 |F|R|R|R| opcode|M| Payload len |    Extended payload length    |
 |I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
 |N|V|V|V|       |S|             |   (if payload len==126/127)   |
 | |1|2|3|       |K|             |                               |
 +-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
 |     Extended payload length continued, if payload len == 127  |
 + - - - - - - - - - - - - - - - +-------------------------------+
 |                               |Masking-key, if MASK set to 1  |
 +-------------------------------+-------------------------------+
 | Masking-key (continued)       |          Payload Data         |
 +-------------------------------- - - - - - - - - - - - - - - - +
 :                     Payload Data continued ...                :
 + - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
 |                     Payload Data continued ...                |
 +---------------------------------------------------------------+
```
- FIN： 1 bit 。表示此帧是否是消息的最后帧，第一帧也可能是最后帧。  
- RSV1，RSV2，RSV3： 各1 bit 。必须是0，除非协商了扩展定义了非0的意义。
- opcode：4 bit。表示被传输帧的类型：x0 表示一个后续帧；x1 表示一个文本帧；x2 表示一个二进制帧；x3-7 为以后的非控制帧保留；x8 表示一个连接关闭；x9 表示一个ping；xA 表示一个pong；xB-F 为以后的控制帧保留。  
- Mask： 1 bit。表示净荷是否有掩码（只适用于客户端发送给服务器的消息）。  
- Payload length： 7 bit, 7 + 16 bit, 7 + 64 bit。   净荷长度由可变长度字段表示： 如果是 0~125，就是净荷长度；如果是 126，则接下来 2 字节表示的 16 位无符号整数才是这一帧的长度； 如果是 127，则接下来 8 字节表示的 64 位无符号整数才是这一帧的长度。  
- Masking-key：0或4 Byte。 用于给净荷加掩护，客户端到服务器标记。  
- Extension data： x Byte。默认为0 Byte，除非协商了扩展。  
- Application data： y Byte。 在”Extension data”之后，占据了帧的剩余部分。  
- Payload data： (x + y) Byte。”extension data” 后接 “application data”。

####  参考如下：

[WebSocket 浅析](https://mp.weixin.qq.com/s/7aXMdnajINt0C5dcJy2USg)

[Netty-Websocket 根据URL路由，分发机制的实现](https://cloud.tencent.com/developer/article/1032466)

[netty](http://www.tianshouzhi.com/api/tutorials/netty/221)  

[WebSocket 协议深入探究](https://www.infoq.cn/article/deep-in-websocket-protocol/)

[学习WebSocket协议—从顶层到底层的实现原理（修订版）](https://github.com/abbshr/abbshr.github.io/issues/22)

[基于Redis以及WebSocket的一个实时消息推送系统](https://ifconfiger.com/articles/push-message-with-redis-and-websocket)