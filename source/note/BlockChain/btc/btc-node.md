# BTC docker 运行节点

## Docker 启动

#### testnet

> 目前BTC测试网数据，大约占据了32G 硬盘存储空间，耗费大约80分钟

```
docker run --name btc-test-node -p 18332:18332  -d fpchen/btc-testnet:m1
```

#### regtest

```
docker run --name btc-dev-node -p 18443:18443  -d fpchen/btc-regtest:m1
```



## 程序启动

- 1、配置文件, 编辑 `/etc/bitcoin/bitcoin.conf`

  ```toml
  daemon=1
  server=1
  rpcuser=test
  rpcpassword=test
  regtest=1
  txindex=1
  rpcallowip=0.0.0.0/0
  discover=0
  listen=0
  ```

  

- 2、启动本地私链

  ```shell
  ➜ bitcoind -conf=/etc/bitcoin/bitcoin.conf
  Bitcoin Core starting
  ```

  

- 3、获取`bitcoind` 监听的端口,  本地一般是 18843

  ```shell
  ➜  netstat --ip -lpa | grep bitcoind
  tcp   0  0   localhost:18443     0.0.0.0:*       LISTEN      6768/bitcoind
  ```

  

- 4、发送请求, 测试服务是否运行

  ```shell
  ➜  curl --request POST \
      --user test:test \
      --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "getblockchaininfo", "params": [] }' \
      -H 'content-type: applicaiton/json;' \
      http://127.0.0.1:18443/
  {
  	"result": {
  		"chain": "regtest",
  		"blocks": 303,
  		"headers": 303,
  		"bestblockhash": "5eba253aed009e25d347d59906c39bf47ae13ca7dc6ccd58c41edd549dd06214",
  		"difficulty": 4.656542373906925e-10,
  		"mediantime": 1600689629,
  		"verificationprogress": 1,
  		"initialblockdownload": false,
  		"chainwork": "0000000000000000000000000000000000000000000000000000000000000260",
  		"size_on_disk": 91959,
  		"pruned": false,
  		"softforks": {
  			.......
  		},
  		"warnings": ""
  	},
  	"error": null,
  	"id": "curltest"
  }
  ```

  

- 5、导入私钥进钱包, 默认钱包名称为 ""

  ```shell
  ➜ bitcoin-cli -conf=/etc/bitcoin/bitcoin.conf  -rpcwallet="" importprivkey "cUDfdzioB3SqjbN9vutRTUrpw5EH9srrg6RPibacPo1fGHpfPKqL"
  ```

  

- 6、构造生成块,  需要生成101个块, 如果需要使用coinbase交易, 需要100个块后确认, 最好多于100个块

  ```shell
  ➜  bitcoin-cli -conf=/etc/bitcoin/bitcoin.conf generatetoaddress 101 mvuTXVzk7n9QYHMhyUUfaPdeQ4QVwA2fmT
  ```

  

- 7、根据hash `2d9ce904ac4d0df8dffec9a9a7e2c65883c357c37bceab044fb70f3515f9720c`查询块内交易

  ```shell
  ➜  bitcoin-cli -conf=/etc/bitcoin/bitcoin.conf getblock 2d9ce904ac4d0df8dffec9a9a7e2c65883c357c37bceab044fb70f3515f9720c
  {
    "hash": "2d9ce904ac4d0df8dffec9a9a7e2c65883c357c37bceab044fb70f3515f9720c",
    "confirmations": 196,
    "strippedsize": 217,
    "size": 253,
    "weight": 904,
    "height": 108,
    "version": 536870912,
    "versionHex": "20000000",
    "merkleroot": "d0bce39e8a8a52ec58e71cb0acc28f21a2d54917e9c201619454d65078766ce4",
    "tx": [
      "d0bce39e8a8a52ec58e71cb0acc28f21a2d54917e9c201619454d65078766ce4"
    ],
    "time": 1600689597,
    "mediantime": 1600689596,
    "nonce": 0,
    "bits": "207fffff",
    "difficulty": 4.656542373906925e-10,
    "chainwork": "00000000000000000000000000000000000000000000000000000000000000da",
    "nTx": 1,
    "previousblockhash": "642bf8c9135ef0fc37799a7348ecbc5d4e70a89cfce7e59586ad6fe34b64e093",
    "nextblockhash": "1f767a69b1c168ba55ade509c2b5cca11d848672e331a91dc5035778b243c0a7"
  }
  
  ```

  

- 8、根据交易hash `d0bce39e8a8a52ec58e71cb0acc28f21a2d54917e9c201619454d65078766ce4` 查询交易

  ```shell
  ➜  bitcoin-cli -conf=/etc/bitcoin/bitcoin.conf gettxout d0bce39e8a8a52ec58e71cb0acc28f21a2d54917e9c201619454d65078766ce4 0
  {
    "bestblock": "5eba253aed009e25d347d59906c39bf47ae13ca7dc6ccd58c41edd549dd06214",
    "confirmations": 196,#coinbase 交易需要100个确认才能使用
    "value": 50.00000000,
    "scriptPubKey": {
      "asm": "OP_DUP OP_HASH160 a8cb707e4d0a5c6e690189bc0065a8f787aabced OP_EQUALVERIFY OP_CHECKSIG",
      "hex": "76a914a8cb707e4d0a5c6e690189bc0065a8f787aabced88ac",
      "reqSigs": 1,
      "type": "pubkeyhash",
      "addresses": [
        "mvuTXVzk7n9QYHMhyUUfaPdeQ4QVwA2fmT"
      ]
    },
    "coinbase": true
  }
  ```



## Docker 脚本

> 主要以测试网为主，私链无所谓配置

- bitcoin.conf

  ```shell
  daemon=1
  server=1
  rpcuser=axontest
  rpcpassword=axontest
  txindex=1
  testnet=1
  fallbackfee=0.02
  datadir=/data/bitcoin/bitcoin-data
  
  [test]
  rpcallowip=0.0.0.0/0
  rpcbind=0.0.0.0
  rpcport=18332
  addnode=47.100.162.210
  addnode=114.214.228.185 
  # https://bitnodes.io/#join-the-network 查找可用节点同步数据
  ```

  

- Dockerfile

  ```dockerfile
  FROM ubuntu:18.04
  ADD https://bitcoin.org/bin/bitcoin-core-0.20.0/bitcoin-0.20.0-x86_64-linux-gnu.tar.gz .
  RUN tar -xzvf bitcoin-0.20.0-x86_64-linux-gnu.tar.gz -C ./
  ADD entrypoint.sh ./
  ADD bitcoin.conf /etc/bitcoin/bitcoin.conf
  user root
  RUN chmod 777 ./entrypoint.sh
  RUN chmod go-w /etc/bitcoin/bitcoin.conf
  RUN mkdir -p /data/bitcoin/bitcoin-data
  RUN chown -R 755 /data/bitcoin/bitcoin-data
  
  EXPOSE 18332
  ENTRYPOINT ["./entrypoint.sh"]
  ```

- 启动脚本

  ```shell
  #!/bin/bash
  
  export PATH=/bitcoin-0.20.0/bin:$PATH
  
  bitcoind --conf=/etc/bitcoin/bitcoin.conf  
  echo "wait 90 sec for bitcoind start" # 需要等一会儿确保服务启动
  sleep 90
  
  bitcoin-cli -conf=/etc/bitcoin/bitcoin.conf createwallet miner
  bitcoin-cli -conf=/etc/bitcoin/bitcoin.conf -rpcwallet="miner" importprivkey "cURtxPqTGqaA5oLit5sMszceoEAbiLFsTRz7AHo23piqamtxbzav"
  
  bitcoin-cli  -conf=/etc/bitcoin/bitcoin.conf getnetworkinfo # network 
  bitcoin-cli  -conf=/etc/bitcoin/bitcoin.conf getpeerinfo # peer info
  bitcoin-cli  -conf=/etc/bitcoin/bitcoin.conf getblockchaininfo # verificationprogress 代表区块同步进度
  
  tail -f /data/bitcoin/bitcoin-data/testnet3/debug.log # 同步的日志所在位置
  ```

  