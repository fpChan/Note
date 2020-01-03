# redis 应用场景

### 一、分布式锁

### 二、数据存储

redis 可用作数据缓存，包括五种类型：

- **String:**

  Strings 数据结构是简单的key-value类型，value其实不仅是String，也可以是数字。

  常用命令:  set,get,decr,incr,mget 等。

  应用场景：String是最常用的一种数据类型，普通的key/ value 存储都可以归为此类.即可以完全实现目前 Memcached 的功能，并且效率更高。还可以享受Redis的定时持久化，操作日志及 Replication等功能。除了提供与 Memcached 一样的get、set、incr、decr 等操作外，Redis还提供了下面一些操作：

  　    获取字符串长度

  　　往字符串append内容

  　　设置和获取字符串的某一段内容

  　　设置及获取字符串的某一位（bit）

  　　批量设置一系列字符串的内容

   实现方式：String在redis内部存储默认就是一个字符串，被redisObject所引用，当遇到incr,decr等操作时会转成数值型进行计算，此时redisObject的encoding字段为int。

​       **扩容过程**：   

​               当len 长度小于1M时，扩容时双倍扩容

​                当len 长度大于1M时，每次扩容1M容量

- **Hash：**

  Redis的Hash实际是内部存储的Value为一个HashMap，并提供了直接存取这个Map成员的接口，如下图：

  　　![img](https://images2018.cnblogs.com/blog/955092/201806/955092-20180601170837235-127169804.jpg)

  也就是说，Key仍然是用户ID, value是一个Map，这个Map的key是成员的属性名，value是属性值，这样对数据的修改和存取都可以直接通过其内部Map的Key(Redis里称内部Map的key为field), 也就是通过 key(用户ID) + field(属性标签) 就可以操作对应属性数据了，既不需要重复存储数据，也不会带来序列化和并发修改控制的问题。很好的解决了问题。

  常用命令：hget,hset,hgetall 等。

  HSET命令用来给字段赋值，而HGET命令用来获得字段的值。用法如下：

  ```sql
  HSET key field value
  HGET key field
  redis＞HSET car price 500
  (integer) 1
  redis＞HSET car name BMW
  (integer) 1
  redis＞HGET car name
  "BMW"
  
  HMSET key field1 value1 field2 value2
  redis＞HMGET car price name
  1) "500"
  2) "BMW"
  
  ```

  ​        HSET命令的方便之处在于不区分插入和更新操作，这意味着修改数据时不用事先判断字段是否存在来决定要执行的是插入操作（update）还是更新操作（insert）。当执行的是插入操作时（即之前字段不存在）HSET命令会返回1，当执行的是更新操作时（即之前字段已经存在）HSET命令会返回0。更进一步，当键本身不存在时，HSET命令还会自动建立它。

  ​         Redis提供了接口(hgetall)可以直接取到全部的属性数据,但是如果内部Map的成员很多，那么涉及到遍历整个内部Map的操作，由于Redis单线程模型的缘故，这个遍历操作可能会比较耗时，而另其它客户端的请求完全不响应，这点需要格外注意。

  实现方式：

  　　上面已经说到Redis Hash对应Value内部实际就是一个HashMap，实际这里会有2种不同实现，这个Hash的成员比较少时Redis为了节省内存会采用类似一维数组的方式来紧凑存储，而不会采用真正的HashMap结构，对应的value redisObject的encoding为zipmap,当成员数量增大时会自动转成真正的HashMap,此时encoding为ht。

- **List：**

  　　常用命令：lpush,rpush,lpop,rpop,lrange等。

  　　应用场景：

  　　Redis list的应用场景非常多，也是Redis最重要的数据结构之一，比如twitter的关注列表，粉丝列表等都可以用Redis的list结构来实现。

  　　Lists 就是链表，相信略有数据结构知识的人都应该能理解其结构。使用Lists结构，我们可以轻松地实现最新消息排行等功能。Lists的另一个应用就是消息队列，
  可以利用Lists的PUSH操作，将任务存在Lists中，然后工作线程再用POP操作将任务取出进行执行。Redis还提供了操作Lists中某一段的api，你可以直接查询，删除Lists中某一段的元素。

  实现方式：

  　　Redis list的实现为一个双向链表，即可以支持反向查找和遍历，更方便操作，不过带来了部分额外的内存开销，Redis内部的很多实现，包括发送缓冲队列等也都是用的这个数据结构。

- **Set**

  　　常用命令：sadd,spop,smembers,sunion 等。

  　　应用场景：

  　　Redis set对外提供的功能与list类似是一个列表的功能，特殊之处在于set是可以自动排重的，当你需要存         储一个列表数据，又不希望出现重复数据时，set是一个很好的选择，并且set提供了判断某个成员是否在一个set集合内的重要接口，这个也是list所不能提供的。

  　　Sets 集合的概念就是一堆不重复值的组合。利用Redis提供的Sets数据结构，可以存储一些集合性的数据，比如在微博应用中，可以将一个用户所有的关注人存在一个集合中，将其所有粉丝存在一个集合。Redis还为集合提供了求交集、并集、差集等操作，可以非常方便的实现如共同关注、共同喜好、二度好友等功能，对上面的所有集合操作，你还可以使用不同的命令选择将结果返回给客户端还是存集到一个新的集合中。

  　　实现方式：

  　　set 的内部实现是一个 value永远为null的HashMap，实际就是通过计算hash的方式来快速排重的，这也是set能提供判断一个成员是否在集合内的原因。

- **Sorted Set**

  　   常用命令：zadd,zrange,zrem,zcard等

  　　使用场景：

  　　Redis sorted set的使用场景与set类似，区别是set不是自动有序的，而sorted set可以通过用户额外提供一个优先级(score)的参数来为成员排序，并且是插入有序的，即自动排序。当你需要一个有序的并且不重复的集合列表，那么可以选择sorted set数据结构，比如twitter 的public timeline可以以发表时间作为score来存储，这样获取时就是自动按时间排好序的。

  　　另外还可以用Sorted Sets来做带权重的队列，比如普通消息的score为1，重要消息的score为2，然后工作线程可以选择按score的倒序来获取工作任务。让重要的任务优先执行。

  　　实现方式：

  　　Redis sorted set的内部使用HashMap和跳跃表(SkipList)来保证数据的存储和有序，HashMap里放的是成员到score的映射，而跳跃表里存放的是所有的成员，排序依据是HashMap里存的score,使用跳跃表的结构可以获得比较高的查找效率，并且在实现上比较简单。

#### 参考如下：

[Redis之数据存储结构](https://www.cnblogs.com/guanghe/p/9122684.html)

[Redis面试题](https://www.cnblogs.com/guanghe/p/11465540.html)

### 三、消息队列

一般使用list结构作为队列，rpush生产消息，lpop消费消息。当lpop没有消息的时候，要适当sleep一会再重试。

```go
#无限循环读取任务队列中的内容
loop
task=RPOR queue
if task
#如果任务队列中有任务则执行它
execute( task)
else
#如果没有则等待1秒以免过于频繁地请求数据
wait 1 second
```

当任务队列中没有任务时消费者每秒都会调用一次RPOP命令查看是否有新任务。如果可以实现一旦有新任务加入任务队列就通知消费者就好了。其实借助 BRPOP 命令就可以实现这样的需求。

`BRPOP`命令和RPOP命令相似，唯一的区别是当列表中没有元素时BRPOP命令会一直阻塞住连接，在没有消息的时候，它会阻塞住直到有新元素加入。

```
loop
#如果任务队列中没有新任务，BRPOP 命令会一直阻塞，不会执行execute()。
task=BRPOP queue, 0
#返回值是一个数组（见下介绍），数组第二个元素是我们需要的任务。
execute( task[1])
```

BRPOP命令接收两个参数，第一个是键名，第二个是超时时间，单位是秒。当超过了此时间仍然没有获得新元素的话就会返回nil。上例中超时时间为“0”，表示不限制等待的时间，即如果没有新元素加入列表就会永远阻塞下去。



### 四、订阅推送

Pub/Sub 从字面上理解就是发布（Publish）与订阅（Subscribe），在Redis中，你可以设定对某一个key值进行消息发布及消息订阅，当一个key值上进行了消息发布后，所有订阅它的客户端都会收到相应的消息。这一功能最明显的用法就是用作实时消息系统，比如普通的即时聊天，群聊等功能。

“发布/订阅”模式中包含两种角色，分别是发布者和订阅者。订阅者可以订阅一个或若干个频道（`channel`），而发布者可以向指定的频道发送消息，所有订阅此频道的订阅者都会收到此消息。 

pub/sub 在消费者下线的情况下，生产的消息会丢失。

