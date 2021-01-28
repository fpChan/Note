
# pulsar-go

### 客户端

Pulsar协议 url 使用 `pulsar` scheme来指定被连接的集群，默认端口为6650。以下是 `localhost` 的示例:

```http
pulsar://localhost:6650
```

生产环境的Pulsar 集群URL类似这样：

```http
pulsar://pulsar.us-west.example.com:6650
```

### 创建客户端

```go
import (
    "log"
    "runtime"

    "github.com/apache/pulsar/pulsar-client-go/pulsar"
)

func main() {
    client, err := pulsar.NewClient(pulsar.ClientOptions{
        URL: "pulsar://localhost:6650",
        OperationTimeoutSeconds: 5,
        MessageListenerThreads: runtime.NumCPU(),
    })

    if err != nil {
        log.Fatalf("Could not instantiate Pulsar client: %v", err)
    }
}
```

### Producers

```go
producer, err := client.CreateProducer(pulsar.ProducerOptions{
    Topic: "my-topic",
})

if err != nil {
    log.Fatalf("Could not instantiate Pulsar producer: %v", err)
}

defer producer.Close()

msg := pulsar.ProducerMessage{
    Payload: []byte("Hello, Pulsar"),
}

if err := producer.Send(msg); err != nil {
    log.Fatalf("Producer could not send message: %v", err)
}
```

####  Producer operations

| 方法                                                         | 说明：                                                       | 返回类型 |
| :----------------------------------------------------------- | :----------------------------------------------------------- | :------: |
| `Topic()`                                                    | Fetches the producer's [topic](https://pulsar.apache.org/docs/zh-CN/next/reference-terminology#topic) | `string` |
| `Name()`                                                     | Fetches the producer's name                                  | `string` |
| `Send(context.Context, ProducerMessage) error`               | Publishes a [message](https://pulsar.apache.org/docs/zh-CN/next/client-libraries-go/#messages) to the producer's topic. 该调用将一直阻塞，直到Pulsar代理成功确认该消息为止；如果超出了在生产者配置中使用SendTimeout设置的超时设置，则将引发错误。 | `error`  |
| `SendAsync(context.Context, ProducerMessage, func(ProducerMessage, error))` | Publishes a [message](https://pulsar.apache.org/docs/zh-CN/next/client-libraries-go/#messages) to the producer's topic asynchronously. 第三个参数是一个回调函数，它指定在确认消息或引发错误时发生的情况。 |          |
| `Close()`                                                    | 关闭生产者并释放分配给它的所有资源。如果调用Close（），则发布者将不再接受任何消息。该方法将一直阻塞，直到Pulsar保留了所有待处理的发布请求。如果抛出错误，将不会重试任何暂挂写入。 |          |

###  Consumers

消费者订阅一个或多个主题，并听取在该主题/这些主题上产生的传入消息。

```go
msgChannel := make(chan pulsar.ConsumerMessage)

consumerOpts := pulsar.ConsumerOptions{
    Topic:            "my-topic",
    SubscriptionName: "my-subscription-1",
    Type:             pulsar.Exclusive,
    MessageChannel:   msgChannel,
}

consumer, err := client.Subscribe(consumerOpts)

if err != nil {
    log.Fatalf("Could not establish subscription: %v", err)
}

defer consumer.Close()

for cm := range msgChannel {
    msg := cm.Message

    fmt.Printf("Message ID: %s", msg.ID())
    fmt.Printf("Message value: %s", string(msg.Payload()))

    consumer.Ack(msg)
}
```

#### Consumer operations

| 方法                         | 说明：                                                       |      返回类型      |
| :--------------------------- | :----------------------------------------------------------- | :----------------: |
| `Topic()`                    | Returns the consumer's [topic](https://pulsar.apache.org/docs/zh-CN/next/reference-terminology#topic) |      `string`      |
| `Subscription()`             | Returns the consumer's subscription name                     |      `string`      |
| `Unsubcribe()`               | 取消订阅分配的主题。如果取消订阅操作不成功，则会引发错误     |      `error`       |
| `Receive(context.Context)`   | 从主题接收一条消息。此方法将阻塞，直到出现消息为止           | `(Message, error)` |
| `Ack(Message)`               | [Acknowledges](https://pulsar.apache.org/docs/zh-CN/next/reference-terminology#acknowledgment-ack) a message to the Pulsar [broker](https://pulsar.apache.org/docs/zh-CN/next/reference-terminology#broker) |      `error`       |
| `AckID(MessageID)`           | [Acknowledges](https://pulsar.apache.org/docs/zh-CN/next/reference-terminology#acknowledgment-ack) a message to the Pulsar [broker](https://pulsar.apache.org/docs/zh-CN/next/reference-terminology#broker) by message ID |      `error`       |
| `AckCumulative(Message)`     | [Acknowledges](https://pulsar.apache.org/docs/zh-CN/next/reference-terminology#acknowledgment-ack) *all* the messages in the stream, up to and including the specified message. AckCumulative方法将一直阻塞，直到将确认发送到代理为止。此后，将不会将邮件重新传递给使用者。累积确认只能与共享订阅类型一起使用. |      `error`       |
| `Nack(Message)`              | Acknowledge the failure to process a single message.         |      `error`       |
| `NackID(MessageID)`          | Acknowledge the failure to process a single message.         |      `error`       |
| `Close()`                    | Closes the consumer, disabling its ability to receive messages from the broker |      `error`       |
| `RedeliverUnackedMessages()` | Redelivers *all* unacknowledged messages on the topic. In [failover](https://pulsar.apache.org/docs/zh-CN/next/concepts-messaging#failover) mode, 如果使用者未在指定主题上处于活动状态，则将忽略此请求; in [shared](https://pulsar.apache.org/docs/zh-CN/next/concepts-messaging#shared) mode, 重新传递的消息分布在与该主题相关的所有使用者上。注意：这是一个不会引发错误的非阻塞操作。. |                    |

### Readers

Pulsar readers process messages from Pulsar topics

 readers 与  consumers 不同，因为使用读取器，您需要明确指定要从流中开始的消息（另一方面， consumers会自动以最新的未确认消息开始）。

```go
reader, err := client.CreateReader(pulsar.ReaderOptions{
    Topic: "my-golang-topic",
    StartMessageId: pulsar.LatestMessage,
})
```

