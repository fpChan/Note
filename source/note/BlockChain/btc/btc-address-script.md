#  BTC系列之账户脚本

## UXTO 

比特币完整节点跟踪所有可找到的和可使用的输出，称为 “未花费的交易输出”（unspent transaction outputs），即UTXO。 所有UTXO的集合被称为UTXO集，目前有数百万个UTXO。 当新的UTXO被创建，UTXO集就会变大，当UTXO被消耗时，UTXO集会随着缩小。每一个交易都代表UTXO集的变化（状态转换）

<html>
<img src="https://ss.csdn.net/p?http://mmbiz.qpic.cn/mmbiz_png/fcTCLwqsqxOwo64abP7ic2gJsVViaCZHKLjwYNBkaIPUZF6t7fujKMfjhMibe9EEqbEWoDwOQO92oGtianWYjZ1lHQ/640?wx_fmt=png"/>
</html>



```
{
  "version": 1,
  "locktime": 0,
  "vin": [
    {
      "txid":"7957a35fe64f80d234d76d83a2a8f1a0d8149a41d81de548f0a65a8a999f6f18",
      "vout": 0,
      "scriptSig": "3045022100884d142d86652a3f47ba4746ec719bbfbd040a570b1deccbb6498c75c4ae24cb02204b9f039ff08df09cbe9f6addac960298cad530a863ea8f53982c09db8f6e3813[ALL] 0484ecc0d46f1918b30928fa0e4ed99f16a0fb4fde0735e7ade8416ab9fe423cc5412336376789d172787ec3457eee41c04f4938de5cc17b4a10fa336a8d752adf",
      "sequence": 4294967295
    }
 ],
  "vout": [
    {
      "value": 0.01500000,
      "scriptPubKey": "OP_DUP OP_HASH160 ab68025513c3dbd2f7b92a94e0581f5d50f654e7 OP_EQUALVERIFY OP_CHECKSIG"
    },
    {
      "value": 0.08450000,
      "scriptPubKey": "OP_DUP OP_HASH160 7f9b1a7fb68d60c536c2fd8aeaa53a8f3cc025a8 OP_EQUALVERIFY OP_CHECKSIG",
    }
  ]
}

```

#### 交易输出(创世交易先有输出)

```
"vout": [
  {
    "value": 0.01500000,
    "scriptPubKey": "OP_DUP OP_HASH160 ab68025513c3dbd2f7b92a94e0581f5d50f654e7 OP_EQUALVERIFY
OP_CHECKSIG"
  },
  {
    "value": 0.08450000,
    "scriptPubKey": "OP_DUP OP_HASH160 7f9b1a7fb68d60c536c2fd8aeaa53a8f3cc025a8 OP_EQUALVERIFY OP_CHECKSIG",
  }
]
```

#### 交易输入

交易输入将UTXO（通过引用）标记为将被消费，并通过解锁脚本提供所有权证明。

**输入的第一部分是一个指向UTXO的指针，通过指向UTXO被记录在区块链中所在的交易的哈希值和序列号来实现**

```
"vin": [
  {
    "txid": "7957a35fe64f80d234d76d83a2a8f1a0d8149a41d81de548f0a65a8a999f6f18",
    "vout": 0,
    "scriptSig" : "3045022100884d142d86652a3f47ba4746ec719bbfbd040a570b1deccbb6498c75c4ae24cb02204b9f039ff08df09cbe9f6addac960298cad530a863ea8f53982c09db8f6e3813[ALL] 0484ecc0d46f1918b30928fa0e4ed99f16a0fb4fde0735e7ade8416ab9fe423cc5412336376789d172787ec3457eee41c04f4938de5cc17b4a10fa336a8d752adf",
    "sequence": 4294967295
  }
]
```

- 一个交易ID，引用包含正在使用的UTXO的交易
- 一个输出索引（vout），用于标识来自该交易的哪个UTXO被引用（第一个为零）
- 一个 scriptSig（解锁脚本），满足放置在UTXO上的条件，解锁它用于支出
- 一个序列号（稍后讨论）

在 Alice 的交易中，输入指向的交易ID是：

```
7957a35fe64f80d234d76d83a2a8f1a0d8149a41d81de548f0a65a8a999f6f18
```

输出索引是0（即由该交易创建的第一个UTXO）, 那个输出（如上：value）就可以被引用了。

**如果不检索输入中引用的UTXO，则不知道它们的值。因此，在单个交易中计算交易费用的简单操作，实际上涉及多个交易的多个步骤和数据。**



### 比特币交易脚本和脚本语言

#### 脚本构建（锁定与解锁）

- **锁定脚本** 是一个放置在输出上面的花费条件：它指定了今后花费这笔输出必须要满足的条件。 由于锁定脚本往往含有一个公钥或比特币地址（公钥哈希值），在历史上它曾被称为脚本公钥（scriptPubKey）。
- **解锁脚本**是一个“解决”或满足被锁定脚本在一个输出上设定的花费条件的脚本，它将允许输出被消费。解锁脚本是每一笔比特币交易输入的一部分，而且往往含有一个由用户的比特币钱包（通过用户的私钥）生成的数字签名。由于解锁脚本常常包含一个数字签名，因此它曾被称作ScriptSig。


**每一个比特币验证节点会通过同时执行锁定和解锁脚本来验证一笔交易。每个输入都包含一个解锁脚本，并引用了之前存在的UTXO。**

最常见类型的比特币交易（P2PKH:对公钥哈希的付款）的解锁和锁定脚本的示例
<html>
<img src="https://camo.githubusercontent.com/5e6288a0199f0f4d46ebdfd584bb8961df93e1c0/687474703a2f2f75706c6f61642d696d616765732e6a69616e7368752e696f2f75706c6f61645f696d616765732f313738353935392d653430363035353564313462636432382e706e673f696d6167654d6f6772322f6175746f2d6f7269656e742f7374726970253743696d61676556696577322f322f772f31323430"/>
</html>

#### P2PKH（Pay-to-Public-Key-Hash）

```
OP_DUP OP_HASH160 <Cafe Public Key Hash> OP_EQUALVERIFY OP_CHECKSIG
```

脚本中的 Cafe Public Key Hash 即为咖啡馆的比特币地址，但该地址不是基于Base58Check编码
上述锁定脚本相应的解锁脚本是：

```
<Cafe Signature> <Cafe Public Key>
```

将两个脚本结合起来可以形成如下组合验证脚本：

```
<Cafe Signature> <Cafe Public Key> OP_DUP OP_HASH160
<Cafe Public Key Hash> OP_EQUALVERIFY OP_CHECKSIG
```

只有当解锁脚本得到了咖啡馆的有效签名，交易执行结果才会被通过（结果为真）


### 余额计算

为了构建“总接收”数量，区块链浏览器首先解码比特币地址的Base58Check编码，以检索编码在地址中的Bob的公钥的160位哈希值。然后，区块链浏览器搜索交易数据库，使用包含Bob公钥哈希的P2PKH锁定脚本寻找输出。通过总结所有输出的值，浏览器可以产生接收的总值。

区块链接浏览器将当前未被使用的输入保存为一个分离的数据库——UTXO集。为了维护这个数据库，区块链浏览器必须监视比特币网络，添加新创建的UTXO，并在已被使用的UTXO出现在未经确认的交易中时，实时地删除它们。这是一个复杂的过程，不但要实时地跟踪交易在网络上的传播，同时还要保持与比特币网络的共识，确保在正确的链上。有时区块链浏览器未能保持同步，导致其对UTXO集的跟踪扫描不完整或不正确。





## 脚本类型

- 不同的锁定脚本依赖的源数据生成。对应关系如下

| 脚本类型     | 源类型 | 地址长度 |
| ------------ | ------ | -------- |
| `P2PKH`      | 公钥   | 20       |
| `P2SH`       | 脚本   | 20       |
| `P2WPKH`     | 公钥   | 20       |
| `P2WSH`      | 脚本   | 32       |
| `P2SH-P2WSH` | 公钥   | 20       |
| `P2SH-P2WPK` | 脚本   | 20       |

- 地址的表现形式

  实际上我们看到的地址是经过Bash58编码或bech32编码的地址，地址中添加了地址类型和校验码所以不同的地址开头会呈现不同的数值。生成锁定脚本的时候要解码数据并且去掉地址类型码。

  不同地址的标志位对照表如下：

| `地址类型`        | `网络类型` | `对应的地址标志位` | `编码类型` | `说明`                                                       |
| ----------------- | ---------- | ------------------ | ---------- | ------------------------------------------------------------ |
| **`P2PKH`**       | `main`     | `0x00`             | `Base58`   | `支付到比特币地址的交易包含支付公钥哈希脚本（P2PKH）。由P2PKH 脚本锁定的交易输出可以通过给出由相应私钥创建的公钥和数字签名来解锁（消费）` |
|                   | `testnet`  | `0x6F`             | `Base58`   |                                                              |
|                   | `regtest`  | `0x6F`             | `Base58`   |                                                              |
| **`P2SH`**        | `main`     | `0x05`             | `Base58`   | `P2SH 地址是基于Base58 编码的一个含有20 个字节哈希的脚本。P2SH 地址采用“5”前缀。这导致基于Base58 编码的地址以“3”开头。P2SH 地址隐藏了所有的复杂性，因此，运用其进行支付的人将不会看到脚本。` |
|                   | `testnet`  | `0xC4`             | `Base58`   |                                                              |
|                   | `regtest`  | `0xC4`             | `Base58`   |                                                              |
| **`P2WPKH`**      | `main`     | `"bc"`             | `Bech32`   | `P2WPKH地址是脚本做HASH160得到20位的地址经过Bech32编码后显示` |
|                   | `testnet`  | `"tb"`             | `Bech32`   |                                                              |
|                   | `regtest`  | `"bcrt"`           | `Bech32`   |                                                              |
| **`P2WSH`**       | `main`     | `"bc"`             | `Bech32`   | `P2WSH地址是脚本做HASH256得到到32位的地址经过Bech32编码后显示` |
|                   | `testnet`  | `"tb"`             | `Bech32`   |                                                              |
|                   | `regtest`  | `"bcrt"`           | `Bech32`   |                                                              |
| **`P2SH-P2WPKH`** | `main`     | `0x05`             | `Base58`   | `P2SH-P2WPK地址是为了满足旧钱包的需求，将P2WPKH对应的锁定脚本转换到普通的P2SH地址格式。` |
|                   | `testnet`  | `0xC4`             | `Base58`   |                                                              |
|                   | `regtest`  | `0xC4`             | `Base58`   |                                                              |
| **`P2SH-P2WSH`**  | `main`     | `0x05`             | `Base58`   | `P2SH-P2SH地址是为了满足旧钱包的需求，将P2WPKH对应的锁定脚本转换到普通的P2SH地址格式。` |
|                   | `testnet`  | `0xC4`             | `Base58`   |                                                              |
|                   | regtest    | 0xC4               | Base58     |                                                              |

  

## 锁定脚本的结构

- P2PKH：

  是利用公钥的哈希，相对来说比较简单，现在新版本的钱包应用的越来越少。

  `OP_DUP OP_HASH160 OPCODE_LEN ADDR OP_EQUALVERIFY OP_CHECKSIG`

  对应的字节表示 `0x76 0xa9 0x14  20字节地址 0x88 0xac`

  `P2PKH` 长度：25字节

  `OPCODE_LEN`：`0x14` 即 地址 `ADDR` 的长度

  `ADDR`：是由公钥生成的 `20` 字节

- P2SH：

  利用了脚本的哈希，并且锁定脚本相较于P2PKH更加简洁。由于脚本更加复杂，可以根据需要设计不同的逻辑控制，因此应用会被广泛应用。锁定脚本中表示简单，但是赎回脚本和签名处变的复杂了。
  
  `OP_HASH160 OPCODE_LEN ADDR OP_EQUAL`
  
  对应的字节表示:` 0xa9 0x14 20字节地址 0x87`
  
  `P2SH`长度：`23`
  
  `OPCODE_LEN`：`0x14` 即 地址 `ADDR` 的长度
  
  `ADDR`：是由脚本经过 `HASH160` 生成的 `20` 字节

- P2WPKH：

  是隔离见证中公钥地址的表示，格式主要是为了与非隔离见证的锁定脚本区别。旧钱包是不支持的。

  `VER OPCODE_LEN ADDR`

  对应的字节表示 `0x00 0x14 20字节地址`

  `P2WPKH`长度：`22`

  `0x00`: 版本号，固定 `0`

  `OPCODE_LEN`：`0x14` 即 地址 `ADDR` 的长度

  `ADDR`：是由公钥生成的 `20` 字节

- P2WSH：

  是隔离见证中脚本地址的表示，格式主要是为了与非隔离见证的锁定脚本区别。旧钱包是不支持的。因为可以用到复杂脚本，因此可以做复杂逻辑应用。

  `VER OPCODE_LEN ADDR`

  对应的字节表示` 0x00 0x20 32字节地址`

  `P2WSH` 长度：`34`

  `0x00` : 版本号，固定 `0`

  `OPCODE_LEN`：`0x20`即 地址 `ADDR` 的长度

- P2SH-P2WPKH：

  `P2SH-P2WPKH`  是对 `P2WPKH` 进行 `HASH160` 得到 `20` 字节地址，此地址可在 `P2SH` 中应用，与普通的 `P2SH` 地址没有任何区别。

  格式见 `P2SH`

- P2SH-P2WSH

  `P2SH-P2WSH` 是对 `P2WSH`  进行 `HASH160` 得到 `20` 字节地址，此地址可在 `P2SH` 中应用，与普通的 `P2SH`地址没有任何区别。
  
  格式见`P2SH`



## 比特币地址类型：

比特币地址类型分为3种格式： `legacy`  	 `p2sh-segwit`   	`bech32`

- `legacy`  	类型实际上就是取公钥或脚本的HASH160值得到20位字节地址。
- `p2sh-segwit`    对应生成 `P2SH-P2WPKH` 和 `P2SH-P2WSH` 中的地址

- `bech32`       对应生成 `P2WPKH` 和 `P2WSH`中的地址

 

## 隔离见证中的公钥类型

隔离见证中生成地址用到的公钥必须是压缩的公钥，否则可能会无法赎回此地址的币。

隔离见证地址用长度32或20来判定地址是由脚本或公钥生成的，0（版本）开头表示是隔离见证地址。

 

## 脚本中的地址和钱包中的地址区别

  我们在UI上看到的地址是带有地址类型码并且经过Bash58或Bech32编码后的地址的字符串，因此与实际地址长度并不符合。当我们传入此地址后，会解码并去除类型码，并根据类型码生成不同的ScriptPubkey（P2PKH P2SH P2WSH P2WPKH P2SH-P2WSH P2SH-P2WPKH）。

## 各种地址样子如下：

- P2PKH地址：

   显示的地址：mgjswfb6eXcmuJgLxvMxAo1tth2QCyyPYt

实际地址16进制表示：0x0d 0x69 0xe6 0x9c 0x75 0x72 0x53 0x4c 0xa3 0x5d 0xdd 0x12 0x64 0x6f 0x90 0x8b 0xf0 0x7b 0xf7 0xb6

 

- P2SH地址：

显示的地址：2Mz5nE8zyxQDMZawYZ6cqbHZZdkih5CwQjU

实际地址16进制表示：0x4a 0xff 0xa1 0xed 0x45 0x54 0x17 0x5a 0x00 0xd6 0x54 0x78 0x8d 0x34 0xf3 0x13 0xd7 0x38 0x02 0xdd

 

- P2WSH地址：

   显示的地址：bcrt1qja4c5mpjw8hjlatgwud56naunfykxwupk65yev

   实际地址16进制表示：0x14 0x97 0x6b 0x8a 0x6c 0x32 0x71 0xef 0x2f 0xf5 0x68 0x77 0x1b 0x4d 0x4f 0xbc 0x9a 0x49 0x63 0x3b 0x81

 

- P2WPKH地址：

   显示的地址：bcrt1q09zjqeetautmyzrxn9d2pu5c5glv6zcmj3qx5axrltslu90p88pqykxdv4

   实际地址16进制表示：0x20 0x79 0x45 0x20 0x67 0x2b 0xef 0x17 0xb2 0x08 0x66 0x99 0x5a 0xa0 0xf2 0x98 0xa2 0x3e 0xcd 0x0b 0x1b 0x94 0x40 0x6a 0x74 0xc3 0xfa 0xe1 0xfe 0x15 0xe1 0x39 0xc2



## reference

 [比特币锁定脚本及地址解析](http://bitebibudaozhe.com/?p=5499)

