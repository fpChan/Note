# Raft 算法
Raft 协议分为两个阶段

## 一、节点角色
### 角色定义
- **领导者  Leader**
- **候选者 Candidate**
- **追随者 Follower**

### 角色变化
![图 4 ](../../image/consensus/raft/raft-4.png)

服务器状态。**Follower**只响应来自其他服务器的请求。如果**Follower** 接收不到消息，那么他就会变成**Candidate**并发起一次选举。获得集群中大多数选票的**Candidate**将成为**Leader**。在一个任期内，**Leader**一直都会是**Leader**直到自己宕机了。

## 二、RPC 调用

###  AppendEntries RPC
##### 由 **Leader** 负责调用来复制日志指令；也会用作heartbeat


|   参数     |               解释                  |
|------------|-------------------------------------|
|  term      | **Leader**的任期号|
|  leaderId  | **Leader**的 Id，以便于**Follower** 重定向请求 |
|prevLogIndex|上一条目索引                         |
|prevLogTerm |prevLogIndex 条目的任期号            |
|  entries[] |准备存储的日志条目（表示心跳时为空；一次性发送多个是为了提高效率）|
|leaderCommit|**Leader**已经提交的日志的索引值          |

| 返回值| 解释|
|---|---|
|term|当前的任期号，**Leader**据此可更新自身任期|
|success|如果 **Follower** 包含与 prevLogIndex 和 prevLogTerm 吻合的条目，则返回成功|

##### 接收服务器需实现以下处理逻辑：

- 1、如果任期编号比本地小`term < currentTerm`，则返回`false`( 5.1 节讨论 )；
- 2、如果 **Follower** 在 prevLogIndex 索引处不包含 prevLogTerm 任期条目，则返回`false`( 5.3 节讨论 )；
- 3、如果 **Follower**  有条目与新条目冲突(索引相同任期不同)，则删除该条目以及所有后续条目( 5.3 节讨论 )；
- 4、追加所有未在日志中的新条目；
- 5、如果`leaderCommit > commitIndex`,则将 commitIndex 更新为 leaderCommit 以及最后新条目索引两者的较小值；

### RequestVote RPC 
##### 由候选人负责调用用来征集选票

| 参数 | 解释|
|---|---|
|term| **Candidate**的任期号|
|candidateId| 请求选票的**Candidate**的 Id |
|lastLogIndex| **Candidate**的最后日志条目的索引值|
|lastLogTerm| **Candidate**最后日志条目的任期号|

| 返回值| 解释|
|---|---|
|term| 当前任期号，以便于**Candidate**去更新自己的任期号|
|voteGranted| **Candidate**赢得了此张选票时为真|

##### 接收服务器需实现以下处理逻辑：


- 1、 如果`term < currentTerm`返回 false （5.2 节）
- 2、如果 votedFor 为空或者为 candidateId，并且**Candidate**的日志至少和自己一样新，那么就投票给他（5.2 节，5.4 节）

### 所有服务器需遵守的规则：

#### 所有服务器：

* 如果`commitIndex > lastApplied`，那么就 lastApplied 加一，并把`log[lastApplied]`条目应用到状态机中（5.3 节）
* 如果接收到的 RPC 请求或响应中，任期号`T > currentTerm`，那么就令 currentTerm 等于 T，并切换状态为 **Follwer**（5.1 节）

#### **Follwer**（5.2 节）：

* 响应来自 **Candidate** 和 **Leader** 的请求
* 如果在超过选举超时时间的情况之前都没有收到 **Leader** 的心跳，或者是**Candidate**请求投票的，就自己变成 **Candidate**

#### **Candidate**（5.2 节）：

* 在转变成**Candidate**后就立即开始选举过程
	* 自增当前的任期号（currentTerm）
	* 给自己投票
	* 重置选举超时计时器
	* 发送 **RequestVote RPC** 给其他所有服务器
* 如果接收到大多数服务器的选票，那么就变成 **Leader**
* 如果接收到来自新的 **Leader**的  **AppendEntries RPC**，转变成 **Follwer**
* 如果选举过程超时，再次发起一轮选举

#### **Leader**：

* 一旦成为**Leader**：发送空的**AppendEntries RPC** （心跳）给其他所有的服务器；在一定的空余时间之后不停的重复发送，以阻止**Follwer**超时（5.2 节）
*  如果接收到来自客户端的请求：附加条目到本地日志中，在条目被应用到状态机后响应客户端（5.3 节）
*  如果对于一个**Follwer**，最后日志条目的索引值大于等于 nextIndex，即`lastIndex >= nextIndex`, 则发起 **AppendEntries RPC** 追加从 nextIndex 开始的日志条目：
	* 如果成功：更新相应**Follwer**的 nextIndex 和 matchIndex
	* 如果因为日志不一致而失败，减少 nextIndex 重试,直到成功。
* 如果存在一个满足`N > commitIndex`的 N，并且大多数 **Follwer** 的`matchIndex[i] ≥ N`成立，并且`log[N].term == currentTerm`成立，那么令 commitIndex 等于这个 N （5.3 和 5.4 节）



## 阶段操作 

### 选举阶段

Raft 采用 **心跳机制** 来触发 **领袖选举** 。 服务器启动后，开始以 **Follwer**  角色运行。 只要它不断收到来自 **Leader** 或者 **Candidate** 的 RPC 请求，便保持 **Follwer** 状态不变。 **Leader** 发送周期性心跳(不带任何条目的 **AppendEntries RPC** 请求)给所有 **Follwer** ，以保持领导权。 如果 **Follwer** 超过一定时间( 选举超时时间 )没有收到任何通讯，它便假设当前没有可见的的**Leader**，进而发起新选举。

为发起选举，**Follwer**自增自身任期，并转换为 **Candidate**。 随后它为自己投票，同时向其他服务器发起 RequestVote RPC 请求。  **Candidate** 持续这个状态直到发生以下三种情形之一：

 - **Candidate** 赢得选举, 成为**Leader**,随后它向其他所有服务器发送心跳信息，建立领导权并阻止新的选举。
- 另一台机器以**Leader**身份连接**Candidate** ,如果 **Leader** 领袖任期`term`至少与**Candidate** 一样大，**Candidate**便认为 **Leader** 合法，并重回**Follwer**状态。 相反，**Candidate** 将拒绝 RPC 请求并继续保持**Candidate** 状态。
- 超过设定时间但未产生获胜者,开启一次新的选举——自增任期并开始下一轮 RequestVote 请求。


### 日志复制

 **Leader** 被选举出来之后，开始服务客户端请求。 每个客户端请求包含一个可以被复制状态机执行的命令。  **Leader** 将命令最为新条目追加到本地日志，然后并行发起 **AppendEntries RPC** 请求往其他机器复制该条目。 一旦条目安全 完成复制(已复制到过半数机器)， **Leader** 将把条目应用到自己的状态机并将执行结果告知客户端。 如果 **Follwer** 节点宕机、响应缓慢或者网络丢包， **Leader** 将不断重试 AppendEntries RPC 请求(就算已经响应客户端)，直到该节点日志同步。


## 解决问题

### 日志冲突解决
#### 一致性检查
 在发送 **AppendEntries RPC** 的时候，  **Leader** 顺便带上前一日志条目的索引以及任期编号。 **Follwer**  节点如果找不到对应的条目，它将拒绝新条目。

 一致性检查就像一个归纳步骤：一开始空的日志状态肯定是满足日志匹配特性的，然后一致性检查保护了日志匹配特性当日志扩展的时候。因此，每当 **AppendEntries RPC**  返回成功时，领导人就知道跟随者的日志一定是和自己相同的了。

 #### 不一致， **Leader** 强制 **Follwer** 直接复制自己的日志

 ![图 7](../../image/consensus/raft/raft-7.png)

 当顶部**Leader**节点启动后，从属节点日志状态存在各种可能： a-f 。 每个格子表示一个日志条目；数字代表任期。 **Follwer** 节点可能缺失部分日志条目( a-b )； 也可能包含多余的未提交日志； 或者同时出现( e-f )。 举个例子，情景 f 可能是这样产生的： 该服务器是任期 2 的**Leader**，追加了几个条目，但是还没提交就宕机了； 它迅速重启，在任期 3 继续担任**Leader**，又追加了若干条目； 在新条目提交前，服务器再次宕机，错过了接下来几个任期。

为了让 **Follwer** 日志与自己保持一致，**Leader** 需要找到双方最后一个匹配的条目， 从该点开始删除 **Follwer** 所有不一致条目，并发送所有后续条目。 这些操作根据 **AppendEntries RPC** 返回的一致性检查结果视情况执行。 **Leader** 为每台 **Follwer** 维护一个 nextIndex 变量，保存下一个发送给 **Follwer** 的日志条目编号。 当**Leader** 刚开始服务时，将 nextIndex 设置为自己日志中下一个条目的索引( 索引 11 )。 如果 **Follwer** 日志与领袖不一致，下一次 **AppendEntries RPC** 请求一致性检查将失败。 请求被拒绝后，领袖将降低 nextIndex 并重试 **AppendEntries RPC**请求。 最终 nextIndex 将到达一个双方日志都匹配的点(还可以用二分查找加快这个过程)。 这时， **AppendEntries** 请求将成功，请求将删除属下所有有冲突条目并从领袖日志追加新条目(如有)。 一旦 **AppendEntries RPC** 请求成功，意味着属下日志与领袖一致，任期内后续时间也是如此。



### 选举约束
任何依赖领袖的共识算法，**Leader** 必须拥有所有已提交日志条目。

 Raft 采用一种更简化的做法，选举保证新 **Leader** 必须包含先前任期所有已提交条目，无须传输缺失条目。 这意味着，日志条目只有一个流向，从 **Leader** 流向**Follwer**，**Leader** 不会覆盖日志中已存在的条目。

 Raft 通过选举过程阻止**Candidate** 赢得选举，除非它拥有所有已提交日志。 **Candidate** 想赢得选举必须与集群内大多数机器通讯，这意味着每个已提交条目必须出现在这些机器中至少一台。 只要 **Candidate** 日志至少与其他大多数机器一样新( up-to-date )，它便一定拥有所有已提交条目。 **RequestVote RPC** 请求实现这个约束：该请求带有候选人日志信息，其他节点发现自己日志更新(即更加新， more up-to-date )则拒绝投票。

 Raft 以日志最后条目的索引以及任期判断哪个日志更新。 如果最后条目任期不同，则任期靠后的更新； 如果最后条目任期相同索引不同，则索引大(日志更长)的更新。