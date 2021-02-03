### 二维码数据（URL）
Requesting Connection
```
 wc:{topic...}@{version...}?bridge={url...}&key={key...}
```


<font color = red>'pushURL/new' POST body:{bridge,topic=C…,type, token, peerName, language }</font>  
example: Binance WalletConnect URI


```
wc:519591b0-bb20-42bb-ac21-a8916277a7df@1?bridge=https%3A%2F%2Fwallet-bridge.binance.org&key=612bd63e239a8d7e5d47b0d64c4232098323a51a91f767835d207b96fef56cce
```
字段 | note | example
---|---| --- 
wc:	 | 协议（EIP-1328）| wc:
topic |  唯一标识,使用**UUID** | 519591b0-bb20-42bb-ac21-a8916277a7df
version	| 版本 |1
bridge | 编码后的bridge URL | encode(https://Fwallet-bridge.binance.org)
key | 


