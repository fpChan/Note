# BTC系列之隔离见证

## 为什么需要隔离见证

#### 消除交易的延展性

**“Transaction Malleability”是指在 Transaction 被比特币网络确认之前，txid 可能被别人（攻击者）修改。** 

举例来说，A 提交了一个 Transaction（其功能是转移一个 BTC 给 B），记为 tx1，这个交易的 Input 的 scriptSig 字段中包含了 A 的签名。这个 Transation 在打包确认前，攻击者稍微调整一下 scriptSig（比如增加无关紧要的指令，scriptSig 的关键信息 A 的签名是不能变的，因为不能影响到这个交易信息的验证），这时会得到一个新 txid（因为 scriptSig 参与了 txid 的生成），记为 tx2。现在 tx1 和 tx2 都在等待打包确认状态。如果恰好 tx2 被先打包（这很少出现，但可以伪造更多的 tx3，tx4 来增加被先打包的概率），那么 tx1 在验证时就会失败。因为交易 Input 中引用的 UXTO 已经被 tx2 花费了。这样，A 成功转移了一个 BTC 给 B，但 txid 却不是 A 当初提交的那个 tx1 了。当然如要 tx1 被先打包，那么 tx2 会验证失败，这里 txid 还是 A 当初提交的那个 tx1。

Transaction Malleability 为什么会带来问题呢？我们以例子来说明，假设 A 开了一个交易所，而 B 是该交易所的用户。B 以前存入了 100 个 BTC，现在向 A 提出提币申请，A 向 B 转移 100 个 BTC，记下 txid 为 tx1，B 利用 Transaction Malleability，伪造了另外一个交易 tx2。这时恰好 tx2 被先打包了，tx1 失败。B 对 A 说“我没有收到 100 个 BTC”，A 去查询他当时提交的 txid（即 tx1），发现确实 tx1 没有打包，然后再发起一个新交易，向 B 转移 100 BTC。这里，其实 A 已经向 B 转移了 200 BTC。

当然，这种情况是可以避免的。如果 A 不根据 txid 来判断是否转账成功，而是查询它钱包地址的余额变化，那么他是可以发现已经转移过 100 个 BTC 给用户 B 了（只是 txid 变了而已）。

**比特币交易平台 Mt.Gox，曾经由于 Transaction Malleability 而损失了比特币，参见 [Bitcoin Transaction Malleability and MtGox](https://arxiv.org/pdf/1403.6676v1.pdf)**

采用隔离见证时，由于 scriptSig 信息总是为空，见证数据保存在另外的字段（witness）中，修改见证数据，也不会对 txid 造成变化，所以消除了 Transaction Malleability。

#### 优化交易存储

见证数据通常在交易的总大小中占了很大比重。更复杂的脚本，如用于多签或支付通道的脚本体积会非常大。在某些情况下，这些脚本会占到交易数据的大多数（超过 75%）。通过将见证数据从交易中移出，隔离见证提高了比特币的可扩展性。节点可以在验证签名后删减见证数据。见证数据不再需要发送到所有节点，也不需要被所有节点存储在磁盘上。

#### 签名验证优化

隔离见证升级签名函数（CHECKSIG，CHECKONSIGG 等），以减少算法的计算复杂度。在引入隔离见证之前，用于生成签名的算法需要大量与交易大小成比例的哈希操作。相对于签名操作的数量数据哈希计算复杂度增加到 O(n^2)，给验证签名的所有节点带来了巨大的计算负担。有了隔离见证，算法的复杂度降低到 O(n)。

#### 离线签名改进

隔离见证签名包含由签名的哈希中的每个输入引用的值（金额）。以前，离线签名设备（如硬件钱包）必须在签名交易之前验证每个输入的金额。这通常是通过流式传输大量先前作为输入引用的交易的数据来实现的。由于金额现在是已签名的提交哈希的一部分，因此离线设备不需要以前的交易。如果金额不匹配（由被入侵的在线系统篡改），签名将是无效的。



## 隔离见证交易案例

从某个地址往 `mno5h3qJZ3cT1TtfJZVErzFkF2BJQTkJMh` 转账 `0.01 BTC`

- p2pkh. 

  ```shell
  bitcoin-cli getrawtransaction 2b95053f3f0f59d358e1afb12bd8153245405954e8dcd6eca8b82daf02adae71 2
  {
    "txid": "2b95053f3f0f59d358e1afb12bd8153245405954e8dcd6eca8b82daf02adae71",
    "hash": "2b95053f3f0f59d358e1afb12bd8153245405954e8dcd6eca8b82daf02adae71",
    "version": 2,
    "size": 226,
    "vsize": 226,
    "weight": 904,
    "locktime": 0,
    "vin": [
      {
        "txid": "04c718ae8f34024f0b0650cf2f8ebd40c63214e5fa8836206bedca26650f29c2",
        "vout": 0,
        "scriptSig": {
          "asm": "3045022100b84617263695d31407d6ae230d3b629d071e65d936ee946c8adf84304163cb2d022045435bf766cfcf5a9e515e43969df06bc13c0e93d0787e0f80a7dcc3c236ac8c[ALL] 029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de7823",
          "hex": "483045022100b84617263695d31407d6ae230d3b629d071e65d936ee946c8adf84304163cb2d022045435bf766cfcf5a9e515e43969df06bc13c0e93d0787e0f80a7dcc3c236ac8c0121029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de7823"
        },
        "sequence": 4294967295
      }
    ],
    "vout": [
      {
        "value": 0.01000000,
        "n": 0,
        "scriptPubKey": {
          "asm": "OP_DUP OP_HASH160 4fd5b5cbe9d25a7cbbef9847d1a6e97d8a076975 OP_EQUALVERIFY OP_CHECKSIG",
          "hex": "76a9144fd5b5cbe9d25a7cbbef9847d1a6e97d8a07697588ac",
          "reqSigs": 1,
          "type": "pubkeyhash",
          "addresses": [
            "mno5h3qJZ3cT1TtfJZVErzFkF2BJQTkJMh"
          ]
        }
      },
      {
        "value": 0.98997750,
        "n": 1,
        "scriptPubKey": {
          "asm": "OP_DUP OP_HASH160 db9d0eb300a248a494f55ec1abb140d5d580216f OP_EQUALVERIFY OP_CHECKSIG",
          "hex": "76a914db9d0eb300a248a494f55ec1abb140d5d580216f88ac",
          "reqSigs": 1,
          "type": "pubkeyhash",
          "addresses": [
            "n1YARc5gEby2WPf81yPUzBDaCHTvRBtTus"
          ]
        }
      }
    ],
    "hex": "0200000001c2290f6526caed6b203688fae51432c640bd8e2fcf50060b4f02348fae18c704000000006b483045022100b84617263695d31407d6ae230d3b629d071e65d936ee946c8adf84304163cb2d022045435bf766cfcf5a9e515e43969df06bc13c0e93d0787e0f80a7dcc3c236ac8c0121029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de7823ffffffff0240420f00000000001976a9144fd5b5cbe9d25a7cbbef9847d1a6e97d8a07697588acf695e605000000001976a914db9d0eb300a248a494f55ec1abb140d5d580216f88ac00000000",
    "blockhash": "047ec3252f08ace282415d5d25ac1ff9eb9dfb55b73612888ee595c55cee6b00",
    "confirmations": 395,
    "time": 1617772888,
    "blocktime": 1617772888
  }
  ```

  

- p2wpkh

  ```shell
   bitcoin-cli getrawtransaction 3dbdf66064a5dd8414f4afea80f2cd318991fef28fb9dbbf491b0e7f58d6226e 2
  {
    "txid": "3dbdf66064a5dd8414f4afea80f2cd318991fef28fb9dbbf491b0e7f58d6226e",
    "hash": "03dcdd25e721f4090ce0123917b2db94019bd1290cfb3af128e712a993f3f1e6",
    "version": 2,
    "size": 225,
    "vsize": 144,
    "weight": 573,
    "locktime": 0,
    "vin": [
      {
        "txid": "c320be2f30ab7e35975133b30adb8b804e580f674dda78d34b199b7da915df97",
        "vout": 0,
        "scriptSig": {
          "asm": "",
          "hex": ""
        },
        "txinwitness": [
          "304402201e9df1d606a9fcbd159b62f1fd0675ba31092ef9d8faf8afa09b48c765d40c74022016f272575b03e22c1eea897d4fe7f88de345c03c3678ae09187141c0617042c701",
          "029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de7823"
        ],
        "sequence": 4294967295
      }
    ],
    "vout": [
      {
        "value": 0.01000000,
        "n": 0,
        "scriptPubKey": {
          "asm": "OP_DUP OP_HASH160 4fd5b5cbe9d25a7cbbef9847d1a6e97d8a076975 OP_EQUALVERIFY OP_CHECKSIG",
          "hex": "76a9144fd5b5cbe9d25a7cbbef9847d1a6e97d8a07697588ac",
          "reqSigs": 1,
          "type": "pubkeyhash",
          "addresses": [
            "mno5h3qJZ3cT1TtfJZVErzFkF2BJQTkJMh"
          ]
        }
      },
      {
        "value": 0.98997740,
        "n": 1,
        "scriptPubKey": {
          "asm": "0 db9d0eb300a248a494f55ec1abb140d5d580216f",
          "hex": "0014db9d0eb300a248a494f55ec1abb140d5d580216f",
          "reqSigs": 1,
          "type": "witness_v0_keyhash",
          "addresses": [
            "bcrt1qmwwsavcq5fy2f984tmq6hv2q6h2cqgt06jy455"
          ]
        }
      }
    ],
    "hex": "0200000000010197df15a97d9b194bd378da4d670f584e808bdb0ab3335197357eab302fbe20c30000000000ffffffff0240420f00000000001976a9144fd5b5cbe9d25a7cbbef9847d1a6e97d8a07697588acec95e60500000000160014db9d0eb300a248a494f55ec1abb140d5d580216f0247304402201e9df1d606a9fcbd159b62f1fd0675ba31092ef9d8faf8afa09b48c765d40c74022016f272575b03e22c1eea897d4fe7f88de345c03c3678ae09187141c0617042c70121029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de782300000000",
    "blockhash": "208069b14e551149519671300e80419f944439cfc76c2a99dc16fd5a99502db0",
    "confirmations": 302,
    "time": 1617772939,
    "blocktime": 1617772939
  }
  ```

  

## 隔离见证规范

### 数据结构

在交易中新增了一个数据结构： witness，下面展示新旧数据结构

```
old: [nVersion] 								[input num] [tx inputs] [output num] [tx outputs] 				 [nLockTime]

new: [nVersion] [marker] [flag] [input num] [tx inputs] [output num] [tx outputs] [witness][nLockTime]
```

以上面的交易数据为例，具体解析如下：

- P2PKH

  ```
  [nVersion] [input num] [tx inputs] [output num] [tx outputs] [nLockTime]
  ```

  - rawtranasaction

    ```
    0200000001c2290f6526caed6b203688fae51432c640bd8e2fcf50060b4f02348fae18c704000000006b483045022100b84617263695d31407d6ae230d3b629d071e65d936ee946c8adf84304163cb2d022045435bf766cfcf5a9e515e43969df06bc13c0e93d0787e0f80a7dcc3c236ac8c0121029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de7823ffffffff0240420f00000000001976a9144fd5b5cbe9d25a7cbbef9847d1a6e97d8a07697588acf695e605000000001976a914db9d0eb300a248a494f55ec1abb140d5d580216f88ac00000000
    ```

    

  - 解析具体字段

    ```
    02000000 	       		// nVersion
    01				       		// input number
    c2290f6526caed6b203688fae51432c640bd8e2fcf50060b4f02348fae18c704 // 小端序的 previous tx hash
    00000000        		// tx vin index
    6b									//解锁脚本长度 10进制 107
    483045022100b84617263695d31407d6ae230d3b629d071e65d936ee946c8adf84304163cb2d022045435bf766cfcf5a9e515e43969df06bc13c0e93d0787e0f80a7dcc3c236ac8c0121029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de7823
    
    ffffffff      		 	// sequence 通常为0xFFFFFFFF。除非事务的锁定时间> 0，否则不相关
    02						 			// output num
    40420f00000000001976a9144fd5b5cbe9d25a7cbbef9847d1a6e97d8a07697588ac
    f695e605000000001976a914db9d0eb300a248a494f55ec1abb140d5d580216f88ac
    00000000     			 // nLockTime 定义交易有效（或最小块高）的最早时间
    ```

    

- P2WPKH

  ```
  [nVersion] [marker] [flag] [input num] [tx inputs] [output num] [tx outputs] [witness][nLockTime]
  ```

  

  - rawtranasaction

    ```
    0200000000010197df15a97d9b194bd378da4d670f584e808bdb0ab3335197357eab302fbe20c30000000000ffffffff0240420f00000000001976a9144fd5b5cbe9d25a7cbbef9847d1a6e97d8a07697588acec95e60500000000160014db9d0eb300a248a494f55ec1abb140d5d580216f0247304402201e9df1d606a9fcbd159b62f1fd0675ba31092ef9d8faf8afa09b48c765d40c74022016f272575b03e22c1eea897d4fe7f88de345c03c3678ae09187141c0617042c70121029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de782300000000
    ```

  - 解析具体字段

    ```
    02000000						// nVersion
    00									// marker 必须是 0
    01									// flag 必须是 1
    01
    97df15a97d9b194bd378da4d670f584e808bdb0ab3335197357eab302fbe20c3 // 小端序的 previous tx hash
    00000000						// tx vin index
    00									// 解锁脚本长度为0，因为在 witness 字段
    ffffffff  					// sequence 通常为0xFFFFFFFF。除非事务的锁定时间> 0，否则不相关
    02									// output num 
    40420f00000000001976a9144fd5b5cbe9d25a7cbbef9847d1a6e97d8a07697588ac
    ec95e60500000000160014db9d0eb300a248a494f55ec1abb140d5d580216f
    
    02			 						// txinwitness 有2部分
    47       						//  txinwitness 签名部分的长度. 10进制 71
    304402201e9df1d606a9fcbd159b62f1fd0675ba31092ef9d8faf8afa09b48c765d40c74022016f272575b03e22c1eea897d4fe7f88de345c03c3678ae09187141c0617042c701
    21									//  txinwitness 公钥部分的长度. 10	进制 33
    029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de7823
    00000000  					// nLockTime 定义交易有效（或最小块高）的最早时间
    ```



### 锁定脚本与验证脚本

#### P2WPKH

- 对应字段

  ```
      witness:      <signature> <pubkey>
      scriptSig:    (empty)
      scriptPubKey: 0 <20-byte-key-hash>
                    (0x0014{20-byte-key-hash})
  ```

  以上述的交易为例

  ```json
      witness:      [
  "304402201e9df1d606a9fcbd159b62f1fd0675ba31092ef9d8faf8afa09b48c765d40c74022016f272575b03e22c1eea897d4fe7f88de345c03c3678ae09187141c0617042c701",
          "029ba616506337ff7f0ccaac35938af4ba614b9853d670c4a45d830d7d38de7823"
        ]
      scriptSig:    (empty)
      scriptPubKey: 0014db9d0eb300a248a494f55ec1abb140d5d580216f
  ```

  

- 实际验证的脚本

  ```
      <signature> <pubkey> CHECKSIG
  ```

  



### txid 与  hash

每个交易存在 hash 和 txid. 	txid 不对 witness 数据也进行 double sha256，这样 witness 数据即便是修改了，也无法影响 txid。

- txid

  ```
  double sha256([nVersion] [input num] [tx inputs] [output num] [tx outputs] [nLockTime])
  ```

- hash

  ```
  double sha256([nVersion] [marker] [flag] [input num] [tx inputs] [output num] [tx outputs] [witness][nLockTime])
  ```

  





## 区块变相扩容

原本 Block 的大小限制为1,000,000字节（1MB）.

BIP 141 提出一种新的计算方式：weight. 新的 Block 限制为 4M weight.

```
weight =  (tx_size - witness_size) * 3 + tx_size < 4M
```

具体对应字段如下所示：

|        | nVersion | marker | flag | input_num | tx_inputs | output_num | tx_outputs | witness | nLockTime |
| :----: | :------: | :----: | :--: | :-------: | :-------: | :--------: | :--------: | :-----: | :-------: |
| weight |    4     |   1    |  1   |     4     |     4     |     4      |     4      |    1    |     4     |

换句话说，`witness_size` 包含了 `marker`   `flag`  `witness`     1 byte 就对应到 1 weight

如果是 non-witness program 則 1 byte 就占了 4 weight.

例如上面例子: 从某个地址往 `mno5h3qJZ3cT1TtfJZVErzFkF2BJQTkJMh` 转账 `0.01 BTC`。

|            | p2pkh                                | p2wpkh                                         |
| ---------- | ------------------------------------ | ---------------------------------------------- |
| From 地址  | `n1YARc5gEby2WPf81yPUzBDaCHTvRBtTus` | `bcrt1qmwwsavcq5fy2f984tmq6hv2q6h2cqgt06jy455` |
| 转账前余额 | `1 BTC`                              | `1 BTC`                                        |
| 转账后余额 | `0.98997750 BTC`                     | `0.98997740 BTC`                               |
| size       | `226 bytes`                          | `225 bytes`                                    |
| weight     | `904`                                | `573`                                          |

- p2pkh 计算 weight

  ```
  (226  - 0) * 3 + 226 = 904
  ```

- p2wpkh 计算 weight

  ```
  weight = (tx_size[225] - marker[1] - flag[1] - txinwitness[1 + 1 + 73 + 1 + 33]) + tx_size[225] 
  (225 - 1 - 1 - 1 - 1 - 71 -1 - 33 ) + 225 = 573
  ```



按照以前的算法，Block 大小限制为1,000,000字节， 最多可以放下

- `1,000,000 / 226 = 4424 `	笔 p2pkh 交易.

- `1,000,000 / 225 = 4444`    笔 p2wpkh 交易. (当然，以前也没有这种交易)

但现在， Block 的 weight 限制为 4 M weight。 

- `4,000,000 / 904 = 4424`	笔 p2pkh 交易. (对于以前的交易存储限制其实并无影响)
- `4,000,000 / 573 = 6980`    笔 p2wpkh 交易. 

相同的目的（转账`0.01BTC`） 可以再一个块内多存储 2千多笔交易，变相的扩容1.5倍了。



## Reference

- [Bitcoin Transactions](https://aandds.com/blog/bitcoin-tx.html)

- [BIP-0141](https://github.com/bitcoin/bips/blob/master/bip-0141.mediawiki)

