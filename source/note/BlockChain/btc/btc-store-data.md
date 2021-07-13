# BTC 系列之数据存储

ETH 可以在交易构造之时直接使用data字段存储数据。BTC 存储数据有不同的方式

## 背景介绍

- dust :  构造交易时，一般认为当交易费用高 于 1/3 交易价值时，即可称作“Dust”或尘埃交易，目前而言，尘埃交易是指交易价值 低于 546 satoshis 比特币(即 0.000000546 BTC)的交易。

- 标准交易和非标准交易

  在比特币中，最常见的交易形式为“鲍勃付爱丽丝（Bob pays Alice）”，它基于“付给*公共密钥哈希*（*P2PKH*）”脚本，该脚本通过发送公钥和由以下人员创建的数字签名来解决：相应的私钥。P2PKH交易只是许多*标准*类别之一：如果交易通过了*Bitcoin Core IsStandard（）*和 *IsStandardTx（）*测试，则该交易为标准交易。但是，通过创建*临时*脚本来锁定（和解锁）交易，还可以生成*非标准的*脚本。交易，但仍可以广播和挖掘。
  
  

## OP_RETURN

op_return 存储的最大字节数设置为83个字节（默认为80个字节，外加3个字节的开销）。

但一个BTC标准交易只能有一个 op_return 的输出。



## OP_DROP

op_drop 运算符删除顶部堆栈元素。

#### P2SH 脚本

构造一个赎回脚本，锁定脚本为其 hash. 解锁脚本需要用这个赎回脚本去验证锁定脚本，同时保障赎回脚本通过。

- 具体脚本

  ```
  赎回脚本  <OP_DUP OP_HASH160  0xca4159109e41b78863d23ceb5493e770cc53c6f4 OP_EQUALVERIFY OP_CHECKSIG>
  解锁脚本  <SIGN> <PUBKEY> <赎回脚本>
  锁定脚本  OP_HASH160 ebcc108d534d6bab12f9f657d29e9c982ea68453 OP_EQUAL
  ```

- 解锁过程

  - 两个脚本经由两步实现组合。 首先，将赎回脚本与锁定脚本比对以确认其与哈希是否匹配:

    ```
    <OP_DUP OP_HASH160  0xca4159109e41b78863d23ceb5493e770cc53c6f4 OP_EQUALVERIFY OP_CHECKSIG> OP_HASH160 ebcc108d534d6bab12f9f657d29e9c982ea68453 OP_EQUAL
    ```

  - 假如赎回脚本与哈希匹配，解锁脚本会被执行以释放赎回脚本

    ```
    <SIGN> <PUBKEY> OP_DUP OP_HASH160  0xca4159109e41b78863d23ceb5493e770cc53c6f4 OP_EQUALVERIFY OP_CHECKSIG
    ```



#### OP_DROP 存储数据

利用 P2SH 脚本，先构造一个由 OP_DROP 和 P2PKH 组合成的赎回脚本。

```
赎回脚本  <OP_DROP OP_DUP OP_HASH160 <PUBKEY>  OP_EQUALVERIFY OP_CHECKSIG>
解锁脚本  <SIGN> <PUBKEY> <DATA> <赎回脚本>
锁定脚本  OP_HASH160 <RedeemScriptHash> OP_EQUAL
```

具体解锁过程如下：

-  首先，将赎回脚本与锁定脚本比对以确认其与哈希是否匹配

  ```
  <OP_DROP OP_DUP OP_HASH160 <PUBKEY>  OP_EQUALVERIFY OP_CHECKSIG> OP_HASH160 <RedeemScriptHash> OP_EQUAL
  ```

- 执行解锁脚本. 上链数据，存储在 Data 字段，这样第一个字段就会被丢弃

  ```
  <SIGN> <PUBKEY> <Data > OP_DROP OP_DUP OP_HASH160  <PUBKEY Hash> OP_EQUALVERIFY OP_CHECKSIG
  ```



## 难题和进度

#### OP_RETURN

每笔交易unlock 2 条 burn tx 记录。 因为  burn tx hash 长度为32，能容纳 2笔。

目前构造的交易 size 大小为 449  byte，按照100聪左右的手续费率，大概每笔 unlock 需要 0.00044900 BTC （蛮贵的）



#### P2SH + OP_DROP

看论文大概能存储 1500左右 字节 的数据

- 多签 unlock 地址会变更，目前尚未测试多签 +  op_drop

目前本地构造的交易，赎回脚本和锁定脚本OK了，但是解锁脚本尚未通过签名验证



#### OP_DROP + P2PKH 

```
解锁脚本  <SIGN> <PUBKEY> <DATA> 
锁定脚本  OP_DROP OP_DUP OP_HASH160 <PUBKEY>  OP_EQUALVERIFY OP_CHECKSIG
```

属于非标准交易，目前尚未找到使矿工节点忽略标准检查，打包非标准交易的方法。



## Reference 

- [Data Insertion in Bitcoin’s Blockchain](https://ledgerjournal.org/ojs/ledger/article/download/101/93/)
- [An Analysis of Non-standard Transactions](https://www.frontiersin.org/articles/10.3389/fbloc.2019.00007/full)