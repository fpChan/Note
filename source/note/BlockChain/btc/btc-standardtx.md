# BTC 系列之标准与非标准交易

## 操作码

| op_code     | details                                                      |
| ----------- | ------------------------------------------------------------ |
| OP_HASH160  | 运算符对顶部堆栈元素进行两次哈希处理：首先使用SHA- 256，然后使用RIPEMD- 160 |
| OP_CHECKSIG | 对整个交易的输出，输入和脚本进行哈希处理。OP_CHECKSIG使用的签名必须是此哈希和公钥的有效签名。如果是，则返回1，否则返回0 |
| OP_MIN      | 运算符将两个顶部元素中较小的一个返回到堆栈中                 |
| OP_DROP     | 运算符删除顶部堆栈元素                                       |
| OP_DEPTH    | 运算符将堆栈元素的数量放入堆栈中                             |
| OP_2DUP     | 运算符在堆栈顶部复制了两个元素                               |



## 标准交易

如果交易的锁定和解锁脚本与一小部分被认为是安全的模板相匹配，则可以被网络接受。这是*isStandard（）*和*isStandardTx（）*测试，通过它的交易称为标准交易。

- 如果所有输出（锁定脚本）仅使用标准交易表单，则*isStandard（）*函数将为TRUE。
- 如果所有输入（解锁脚本）仅根据其花费的输出使用标准交易表单，则*isStandardTx（）*函数将提供TRUE。

定义和检查标准交易背后的主要原因是通过广播有害交易来防止某人攻击比特币。此外，这些检查还使用户无法创建交易，而这会使将来增加新的交易功能更加困难。有七种标准的交易类型。



### **P2PKH (pay to public key hash)**

- 锁定脚本

  ```
  OP_DUP OP_HASH160 <Cafe Public Key Hash> OP_EQUALVERIFY OP_CHECKSIG
  ```

   Cafe Public Key Hash 即为咖啡馆的地址公钥经过OP_HASH160 操作后的数据

- 解锁脚本

  ```
  <Cafe Signature> <Cafe Public Key>
  ```

- 解锁花费 utxo 是的计算过程如下

  ```
  <Cafe Signature> <Cafe Public Key> OP_DUP OP_HASH160 <Cafe Public Key Hash> OP_EQUALVERIFY OP_CHECKSIG
  ```

  只有当解锁脚本得到了咖啡馆的有效签名，交易执行结果才会被通过（结果为 true. 被push 到栈中）



### **P2PK (pay to public key)**

- 锁定脚本

  ```
  <PUBLIC KEY A> OP_CHECKSIG
  ```

  PUBLIC KEY A 即为咖啡馆的地址公钥

- 解锁脚本

  ```
  <A Signature> 
  ```

- 解锁花费 utxo 是的计算过程如下

  ```
  <A Signature> <PUBLIC KEY A> OP_CHECKSIG 
  ```

  只有当解锁脚本得到了咖啡馆的有效签名，交易执行结果才会被通过（结果为 true. 被push 到栈中）



### **multi sign**

*多重签名*脚本设置了一个条件，其中在脚本中记录了*N个*公钥，并且这些签名中至少*M*个必须用于解锁交易。这也称为*N*对*M*方案.

其中*N*是密钥总数，*M*是验证所需签名的下限阈值。当前比特币核心实现的最大*M*为15

- 锁定脚本

  ```
  M <PUBLIC KEY 1> <PUBLIC KEY 2>…<PUBLIC KEY N> N OP_CHECKMULTISIG
  ```

- 解锁脚本

  ```
  OP_0 <SIGNATURE 1> <SIGNATURE 2>…<SIGNATURE M>
  ```

- 解锁花费 utxo 是的计算过程如下。以 3-2 为例

  ```
  OP_0 <SIGNATURE 1> <SIGNATURE 2> 2 <PUBLIC KEY 1> <PUBLIC KEY 2> <PUBLIC KEY 3> 3 OP_CHECKMULTISIG
  ```

  请注意，前缀OP_0是因为在最初的实现中存在错误需要CHECKMULTISIG：由于这个错误，需要在栈上多了一个说法。CHECKMULTISIG只是将其视为占位符。



### **OP_RETURN**

将*数据输出*交易被用来不相关的比特币付款存储数据，任何带有OP_RETURN的输出都证明是不可花费的，无解锁脚本

- 锁定脚本

  ```
  OP_RETURN <DATA>
  ```



### **P2SH (pay to script hash)**

在input，也就是锁定脚本中，包含解锁脚本的hash。

例如，我们可 hash  **5-2多重签名交易**。P2SH等效事务不是“支付给该5键多重签名脚本”，而是“支付给具有此哈希的脚本”。因此，该脚本仅存储20字节的哈希值，而不存储五个pubkey（使用压缩形式大约为180字节）

- 锁定脚本

  ```
  OP_HASH160 <2-OF-5多重签名脚本hash> OP_EQUAL
  ```

- 解锁脚本

  ```
  <SIG1> <SIG2> <2-OF-5多重签名脚本>
  ```

- 解锁花费 utxo 是的计算过程如下。提前构造好赎回脚本(2-OF-5多重签名脚本)

  ```
  <赎回脚本> OP_HASH160 <赎回脚本hash> OP_EQUAL
  ```




### **P2WPKH(pay to witness public key hash)**

- 锁定脚本

  ```
  OP_0 <PUBLIC KEY A HASH> 
  ```

- 解锁脚本(witness 字段)

  ```
  <SIGNATURE S> <PUBLIC KEY A>
  ```

  

### **P2WSH(pay to witness script hash)**



## 非标准交易

交易通过比特币核心参考实现中的*isStandard（）*和*isStandardTx（）*函数进行验证。如果它们没有通过这样的测试，则将它们直接丢弃。但是，有矿工会放弃这些严格检查，这种交易虽说不符合Bitcoin Core强制执行的标准，由于矿工不坚持，其实也可以上链。非标准事务使用更复杂的脚本形式，常见于链上挑战或报备bug。它们的不同在于非标准的input或output 脚本。

正确验证非标准交易会增加创建未来交易的难度，原因有两个：

1.某些脚本可能会损害网络。比如引入复杂验证脚本（需要验证5，6个小时，那节点同步交易之后，出现的空窗期会导致很多孤块产生）

2.一些脚本可能会使将来的升级变得更加困难。



#### **Pay to Public Key Hash 0 [2011]**

它对应于P2PKH的一种失真，不同之处在于，它不是**公共密钥的哈希**，而是一个0值。

锁定脚本的格式为`OP_DUP OP_HASH 160 0 OP_EQUALVERIFY OP_CHECKSIG`。

这些交易是不可花费的，因为作为P2PKH交易，矿工为了验证它们，需要 与锁定脚本中的哈希相对应的公钥，以及生成相应签名的钥。但是，HASH 160返回一个20字节长的哈希：因此，没有任何传递给哈希函数的键可以返回0。一个Bitcointalk线程[16]表示此偏差主要由MtGox执行。产出代表2609.36304319 BTC的价值，当时约为8 000美元（如今约为2000万美元）。

#### **P2PKH NOP [2011，2014]**

此交易与P2PKH相同，唯一的区别是锁定脚本中包含NOP（不执行任何操作的操作）：

`OP_DUP OP_HASH 160 <HASHPUBKEY> OP_EQUALVERIFY OP_CHECKSIG OP_NOP`。

此事务可能用于测试OP_NOP运算符。可以使用与P2PKH相同的脚本将其解锁。

#### **OnlyHash [2011-2014]**

该*OnlyHash*交易在块链的最大量非标准类。这些交易在锁定脚本中包含哈希，通常是文件的哈希，用于使用区块链作为分类账来注册文档。因此，区块链系统的安全性和弹性可以被数字票据服务，证券交易所证书和智能合约之类的应用程序使用。阻止脚本对应于` <HASH-OF-SOMETHING>`。这些事务是在引入OP_RETURN之前使用的，OP_RETURN可以用于相同的目的

#### **P2Pool错误[2012]**

这些交易是由于错误P2Pool中的[19](https://www.frontiersin.org/articles/10.3389/fbloc.2019.00007/full#note19)2012年2月2日至2012年4月1日之间使用[20个](https://www.frontiersin.org/articles/10.3389/fbloc.2019.00007/full#note20)挖矿工具。添加了以下脚本，而不是普通的P2PKH锁定脚本：`OP_IFDUP OP_IF OP_2SWAP OP_VERIFY OP_2OVER OP_DEPTH` 该脚本没有任何意义，甚至无效，因为OP_IF没有被相应的`OP_ENDIF`关闭，可以将其解锁.

####  **OP_CHECKLOCKTIMEVEIRFY OP_DROP（CLTV）[2012] **

在这种情况下，锁定脚本的格式为：` <DATA> OP_CHECKLOCKTIMEVEIRFY OP_DROP`.	所述`OP_CHECKLOCKTIMEVEIRFY`操作者使交易无效的，如果在堆栈的顶部的元件比越大*nLockTime*一个事务的字段。在实践中，使用`OP_CHECKLOCKTIMEVERIFY`可以使资金在未来的某个特定时刻被证明无法使用，即，这是一种将资金冻结到未来某个特定日期的方法。因此，通过对照上述规则检查`<DATA>`元素，我们可以通过使用将TRUE插入堆栈的解锁脚本来验证事务。

#### **OP_MIN OP_EQUAL [2012] **

这些交易相关的脚本` OP_MIN 3 OP_EQUAL `，其仅需要对应于方程两个数 `X ≤  Ŷ  ∧ X  = 3`进行验证。因此，为了解锁，可以将解锁脚本准备为` 3 4`。我们可以将此交易视为如何使用方程式生成比特币交易的证明。这意味着任何人都可以在没有任何私钥的情况下轻松解锁此类交易

##### **Pay to Hash（P2H）[2012-2015] **

这些交易是简单的P2SH交易的简化；我们有一个与P2SH相同的阻止脚本，不同之处在于内部哈希不引用兑换脚本，而是一个十六进制字符串的哈希：` OP_HASH 160 <HASH 160 OFSOMETHING> OP_EQUALVERIFY。` 有两种变体，其中仅散列运算符的类型发生变化：一种对应于HASH 256，而另一种对应于SHA256。两个阻止脚本是` OP_HASH 256 <HASH 256 OFSOMETHING> OP_EQUAL  `和 `OP_SHA 256 <SHA 256 OFSOMETHING> OP_EQUAL。`我们可以将这些交易视为网络中的“竞争”，以在交易中找到哈希值的正确值。

P2H不能被视为*哈希时间锁定合同*（HTLC）。HTLC本质上是一种付款方式，其中两个人同意一种财务安排，其中一方将向另一方支付一定数量的加密货币。但是，接收方只有一定的时间才能接受付款，否则，钱将退还给发送方。取而代之的是，P2H交易与HTLC不同，因为它生成了可以被接收方接受且不受任何时间限制的支付。

这些输出只能通过提供一旦通过加密函数进行哈希处理（称为*hashlock*）等于给定哈希值的数据来使用

验证步骤很简单：阻止脚本中哈希的十六进制字符串足以花费交易

#### **UnLocked（UL）[2015] **

此交易有一个空的锁定脚本：只需将TRUE作为解锁脚本即可将其解锁。几乎所有这些交易的总金额为0 BTC，即它们是无价值的交易。这样的交易除了可以用作交易费之外，还可以用作向矿工捐赠资金的一种方式：进行此类交易的任何矿工还可以包括汇款到他们控制的地址后，再增加。

#### **OP_RETURN ERROR [2016-2017] **

这些事务与OP_RETURN相同，不同之处在于脚本代码中有错误。该代码要求将比实际代码本身更多的操作码压入堆栈。例如，OP RETURN脚本可能要求在代码中插入下一个40个字节，但是如果只有28个字节，则执行失败。该事务显然是由于编程错误引起的。锁定脚本为：`OP_RETURN ERROR `（返回错误）

#### **OP_2 OP_3错误[2017-2018] **

这些事务类似于OP_RETURN错误，但脚本代码中没有OP_RETURN。由于`OP_RETURN ERROR`，他们的代码要求将比代码本身实际字节高一些的字节压入堆栈。这些事务（例如OP_RETURN ERROR）可能与实现错误有关。这是锁定脚本：`OP_2 OP_3 ERROR `（返回错误）





## 支付脚本哈希

正如我们之前介绍的，P2SH事务在其锁定脚本中包含脚本的哈希（称为“*赎回脚本”*）。在区块链中，有149,410,668个P2SH交易，其中花费了140,620,401个（94,12％）。因此，我们决定分析用过的P2SH交易的解锁脚本中的赎回脚本的内容。

### P2SH中的非标准交易

在P2SH中，我们发现111122个非标准交易（占总数的0,08％）；这个数量是我们“简单地”分析区块链（0.02％）时获得的数量的四倍。我们发现了几类新的非标准交易，它们与以前的交易有所不同。

#### OP_CHECKLOCKTIMEVERIFY OP_DROP（CLVT）

我们已经发现了五种不同类型的交易，它们利用了CLVT运算符，正如我们在第7节中已经看到的那样，使得交易在特定日期之前被证明是不可花费的。从本质上讲，它允许用户创建一个比特币交易，其输出仅在将来的某个时候可用。CLTV对于正常运行的支付渠道（例如，闪电网络）是必需的。这些渠道实际上是一系列“脱链”交易，它们受益于典型的链上交易的所有安全性，并具有一些额外的好处[33](https://www.frontiersin.org/articles/10.3389/fbloc.2019.00007/full#note33)。

其中一个等于区块链中已经存在的一组事务：“ <DATA> OP_CHECKLOCKTIMEVEIRFY OP_DROP。” 第二个是用CLVT运算符锁定的P2PK，这是锁定脚本：“ <DATA> OP_CHECKLOCKTIMEVEIRFY OP_DROP <PUBLIC KEY A> OP_CHECKSIG。” 该脚本意味着无法使用签名（与公钥相关）在脚本中的日期之前花费此事务。第三个是用CLVT运算符锁定的P2PKH，这是脚本：“ <DATA> OP_CHECKLOCKTIMEVEIRFY OP_DROP OP_DUP OP_HASH 160 <PUBLIC KEY A HASH> OP_EQUAL OP_CHECKSIG。” 然后我们有一个类“ <DATA> OP_CHECKLOCKTIMEVEIRFY OP_DROP 1 OP_ADD 2 OP_EQUAL“，其仅需要对应于方程式的数目*X* 1 =2∧ *X* = 1：它因此等待直到日期已过期。最后一个是P2PKH变体，它也需要进一步的哈希才能解锁。锁定脚本为“ <DATA> OP_CHECKLOCKTIMEVEIRFY OP_DROP OP_SHA 256 <SHA 256 OFSOMETHING> OP_DUP OP_HASH 160 <PUBLIC KEY A HASH> OP_EQUAL OP_CHECKSIG。” 正如我们可以在看到[图11中](https://www.frontiersin.org/articles/10.3389/fbloc.2019.00007/full#F11)，最经常在交易类型采用的是一个P2PK，几乎1 500输出。

#### OP_DROP

该交易允许在区块链中存储一些数据，而不会使交易变得不可花费。实际上，所有这些事务都以<DATA> OP_DROP开头，其中<DATA>是我们要放入块链中的内容，OP_DROP是将数据从堆栈中删除以便与标准事务相同的运算符。

我们发现了使用OP_DROP的四种不同类型的事务。第一种类型不需要任何解锁，脚本是： <DATA> OP_DROP 1。  然后是2-2多重签名类型 <DATA> OP_DROP 2 <PUBLIC KEY A> <PUBLIC KEY B> 2 OP_CHECKMULTISIG ”，它需要像正常的2-2多重签名一样将两个签名解锁。第三个是带有OP_DROP的P2PKH，由“ <DATA> OP_DROP OP_DUP OP_HASH 160 <PUBLIC KEY A HASH> OP_EQUAL OP_CHECKSIG标识”。同样，对于P2PKH交易，此交易仅需要签名。最后一个是带有P2PK的OP_DROP：“ <DATA> OP_DROP <PUBLIC KEY A> OP_CHECKSIG。

我们可以看到最常用的类型是2 − 2多重签名，几乎有25,000次出现。我们可以说这些交易只是伪装的标准输出，使用OP_DROP运算符添加验证期间丢弃的数据
