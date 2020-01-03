# Netty 实现 webSocket

#### 处理 WebSocket frame
WebSockets 在“帧”里面来发送数据，其中每一个都代表了一个消息的一部分。一个完整的消息可以利用了多个帧。 WebSocket “Request for Comments” (RFC) 定义了六中不同的 frame; Netty 给他们每个都提供了一个 POJO 实现

- CloseWebSocketFrame
- PingWebSocketFrame
- PongWebSocketFrame
- TextWebSocketFrame
- BinaryWebSocketFrame

 其中Close、Ping以及Pong称之为控制帧，Close关闭帧很容易理解，客户端如果接受到了就关闭连接，客户端也可以发送关闭帧给服务端。Ping和Pong是websocket里的心跳，用来保证客户端是在线的。 Text和Binary表示这个传输的帧是文本类型还是二进制类型，二进制类型传输的数据可以是图片或者语音之类的。

###  如何实现消息推送

之前的案例，还是通过客户端发送请求，服务端进行响应的方式进行交互。WebSocket协议还可以实现服务端主动向客户端推送消息的功能。

主动推送需要考虑的问题包括：

**1、服务端要保存用户唯一标记(假设为userId)与其对应的SocketChannel的对应关系，以便之后根据这个唯一标记给用户推送消息。**

对应关系的保存很简单，用一个Map来记录即可。保存这种对应关系的最佳时机是websocket连接刚刚建立的时候，因为这种对应关系只需要保存一次 ，之后就可以拿着这个userId找到对应SocketChannel给用户推送消息。以之前的代码为例，很明显这个操作，应该放在handleHttpRequest方法中处理，因为这个方法在一个websocket连接的生命周期只会调用一次。

我们知道，当连接建立时，我们在服务端就能获取到客户端对应的SocketChannel，我们如果获取到userId呢？WebSocket协议与HTTP协议一样，都支持在url中添加参数。如：

```java
String userId=params.get("userId").get(0);
//保存userId和Channel的对应关系
map.put(userId,ctx.channel());
```

**2、通过userId给用户推送消息**

通常消息推送是由运营人员根据业务需要，从一个后台管理界面，过滤出符合特定条件的用户来推送消息，因此需要推送的userId和推送内容都是运营指定的。推送服务端只需要根据userId找到对应的Channel，将推送消息推送给浏览器即可。代码片段如下：

```java
//运营人员制定要推送的userId和消息
String userId="123456";
String msg="xxxxxxxxxxxxxxxxxxxxxx";
 
//根据userId找到对应的channel，并将消息写出
Channel channel = map.get(userId);
channel.writeAndFlush(new TextWebSocketFrame(msg));
```

一般公司的推送的消息量都比较大，所以需要推送的消息一般会放到一个外部消息队列中，如rocketmq，kafka。推送服务端通过消费这些队列，来给用户推送消息。

**3、客户端ack接受到的消息**

一般情况下，我们会每一个推送的消息都设置一个唯一的msgId。客户端在接受推送的消息后，需要对这条消息进行ack，也就是告诉服务端自己接收到了这条消息，ack时需要将msgId带回来。

如果我们只使用websocket做推送服务，那么之前代码中的handleWebSocketFrame方法，要处理的主要就是这类ack消息。

**4、离线消息**

如果当给某个用户推送消息的时候，其并不在线，可以将消息保存下来，一般都是保存到一个缓存服务器中(如redis)，每次当一个用户与服务端建立连接的时候，首先检查缓存服务器中有没有其对应的离线消息，如果有直接取出来发送给用户。

**5、消息推送记录的存储**

服务端推送完成消息记录之后，还需要将这些消息存储下来，以支持一个用户查看自己曾经受到过的推送消息。

**6、疲劳度控制**

在实现推送功能时，我们通常还会做一个疲劳度控制的功能，也就是限制给一个用户每天推送消息的数量，以免频繁的推送消息给用户造成不好的体验。疲劳度控制可以从多个维度进行设计。例如用户一天可以接受到消息总数，根据业务划分的某种特定类型的消息的一天可以接受到的消息总数等。 



### 参考如下

[Netty 实现 WebSocket 聊天功能](https://waylau.com/netty-websocket-chat/)

[WebSocket协议](http://www.tianshouzhi.com/api/tutorials/netty/341)