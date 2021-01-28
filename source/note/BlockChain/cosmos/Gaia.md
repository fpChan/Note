### Gaia是什么
`gaia`是作为Cosmos SDK应用程序的Cosmos Hub的名称。它有两个主要的入口：

- `gaiad` : Gaia的服务进程，运行着`gaia`程序的全节点。

- `gaiacli` : Gaia的命令行界面，用于同一个Gaia的全节点交互，cli 前端交互

 `gaia`基于Cosmos SDK构建，使用了如下模块

- `x/auth` : 账户和签名,交易有效性检查（签名，随机数，辅助字段），并暴露帐户keeper(可读写修改账户),`keeper`既可以读取和写入所有帐户的所有字段，又可以遍历所有存储的帐户
```
type BaseAccount struct {
  Address       AccAddress
  Coins         Coins
  PubKey        PubKey
  AccountNumber uint64
  Sequence      uint64
}
```
- `x/bank` : token转账,负责处理帐户之间的多资产硬币转移，并跟踪特殊情况下的伪转移，使用auth模块的state(keeper操作)，即对account修改，coin数据存储在account数据结构中。

```
//a multiparty transfer 的 input/output
type Input(Output) struct {
  Address AccAddress
  Coins   Coins
}

type BaseKeeper interface {
  SetCoins(addr AccAddress, amt Coins)
  SubtractCoins(addr AccAddress, amt Coins)
  AddCoins(addr AccAddress, amt Coins)
  InputOutputCoins(inputs []Input, outputs []Output)
}
```



- `x/staking` : 抵押逻辑

- `x/mint` : 增发通胀逻辑

- `x/distribution` : 费用分配逻辑

- `x/slashing` : 处罚逻辑

- `x/gov` : 治理逻辑

- `x/ibc` : 跨链交易

- `x/params` : 处理应用级别的参数
