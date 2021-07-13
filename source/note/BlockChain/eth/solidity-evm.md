### 以太坊EVM的特点

- EVM是一种基于栈的虚拟机（区别于基于寄存器的虚拟机），用于编译、执行智能合约
- EVM是图灵完备的（图灵完备是指：具有无限存储能力的通用物理机器或编程语言，简单来说就是可以解决一切可计算的问题）
- EVM是一个完全隔离的环境，在运行期间不能访问网络、文件，即使不同合约之间也有有限的访问权限
- 操作数栈调用深度为1024   `params.CallCreateDepth 1024`
- 机器码长度一个字节，最多可以有256个操作码

### State Trie全局状态树

| State Trie | value             | 描述说明             |
| :--------- | :---------------- | :------------------- |
| nonce      | RLP(accountState) | 关联block的stateRoot |

### Transactions Trie区块级交易树

| value Trie            | value            | 描述说明                    |
| :-------------------- | :--------------- | :-------------------------- |
| RLP(transactionIndex) | RLP(transaction) | 关联block的transactionsRoot |

### Receipts Trie区块级数据树

| value                 | value                   | 描述说明                |
| :-------------------- | :---------------------- | :---------------------- |
| RLP(transactionIndex) | RLP(transactionReceipt) | 关联block的receiptsRoot |

### Storage Trie全局存储数

| key                                      | value        | 描述说明                     |
| :--------------------------------------- | :----------- | :--------------------------- |
| F(address, storage position,blockNumber) | Storage Data | 关联acountState的storageRoot |

四个Trie 都不在网络传输 ，网络中只传输交易数据



### 三种情况

| 数据逻辑条件                       | a            |
| :--------------------------------- | :----------- |
| tx.to 为有效地址，且 tx.data为空   | 普通转账交易 |
| tx.to 为空，且 tx.data不为空       | 合约创建     |
| tx.to 为有效地址，且 tx.data不为空 | 消息调用     |

### 执行步骤

|      | 逻辑步骤                     | D                                                            |
| :--- | :--------------------------- | :----------------------------------------------------------- |
| 1    | 有效性检查                   | ECRecover(hash(tx),v,r,s)=sender.address 签名恢复成公钥 公钥160位就是地址 tx.nonce=sender.nonce 交易者交易计数 tx.gas0<=tx.gasLimit sender.balance>=tx.gas0*tx.gasPrice block.gasUsed+tx.gas0<=block.gasLimit |
| 2    | 不可撤销的状态修改           | sender.nonce+=1 sender.balance-=tx.gas0*tx.gasPrice          |
| 3    | 转移tx.value (普通转账)      | sender.balance-=tx.balue tx.to.balance+=tx.value             |
| 3    | 执行合约创建（合约创建交易） | 将tx.data作为EVM字节码进行执行                               |
| 3    | 执行消息调用（消息调用交易） | 将tx.data作为ABI编码进行执行                                 |



### EVM代码的执行环境

| 环境要素            | Details                                                      |
| :------------------ | :----------------------------------------------------------- |
| Account State       | 当前执行中会接触到所有账户的状态数据，包括nonce、balance等   |
| Storage State       | 当前执行中会接触到的所有账户的存储数据，即有以太坊客户端独立维护的“仓储树（storage trie）”中给定账户地址对应的存储数据 |
| Block Information   | 即引发当前执行的原始交易所在的区块信息，包括blockhash、coinbase（beneficiary）、timestamp、number、difficulty和gaslimit等 |
| Runtime Environment | 当前执行的一些运行时的参数，包括gasPrice、调用者（直接发起这次调用的地址）和原始调用者（触发这次执行的原始交易发送者地址）等 |

### EVM细节

> - EVM 代码执行的实际gas消耗与其对内存memory的使用有关，并不是固定的。
> - 鼓励最小化使用存储storage，用sstore操作将非0值存储区域重置为0值，会获得实时的gas返还。
> - 交易执行的最后会删除执行过程中接触过的所有“空账户”和自毁列表中的账户，这也会返还一定量的gas。
> - EVM代码的执行必定会持续到一个正常终止或一个异常终止，但无法用代码直接触发一个异常终止。
> - EVM代码执行的异常终止会撤销当前交易中所有对状态的更改，但执行过程中所有消耗的gas不会返还。

## 消息调用

设recipient为消息调用的目标地址，sender为消息调用的发起者地址，code address 为消息调用实际执行的代码所属的地址，我们有4种发起消息调用的方法

| 操作码       | A                                                            |
| :----------- | :----------------------------------------------------------- |
| call         | 向某个接受者地址发起消息调用，recipient（=code address）与sender可以相同，也可以不同，且会根据recipient地址切换执行环境（包含账户状态，存储状态等程序执行所以来的上下文） |
| callcode     | 与call基本等价，但recipient与sender相同且与code address 相同（所以不需要切换执行环境） |
| delegatecall | 与call基本等价，但recipient与sender相同、与code address 不同，不允许进行转账，且执行环境保持不变 |
| staticcall   | 与call基本等价，但不允许进行转账，且不允许对状态state进行任何修改 |

## GHOST 算法

> Greedy Heaviest-Observed Sub-Tree
>
> 分支选举协议
>
> 比特币是最长量分支 10分钟 ，
>
> 以太坊是16秒所以不能最长量

## 执行模型-以太坊虚拟机

### 存储设计

| 存储结构 | A                                                            | A                                                            |
| :------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| ROM      | 用来保存所有EVM程序代码的“只读”存储，由以太坊客户端独立维护  | -                                                            |
| Stack    | 即所谓的“运行栈”，用来保存EVM指令的输入和输出数据            | 最大深度为1024，其中每个单元是个”字（word）256位 32字节“     |
| Momory   | 内存，一个简单的字节数组，用于临时存储EVM代码运行中需要的存取的各种数据 | 基于“字”进行寻址和扩展                                       |
| Storage  | 存储，由以太坊客户端独立维护的持久化数据区域                 | 每个账户的存储区域被以“字”为单位划分为若干”槽（slot）“，合约中的“状态变量”会根据其具体类型分别保存到这些“槽”中 |

### 费用设计

|          | value | instruction                                                  |
| :------- | :---- | :----------------------------------------------------------- |
| Gzero    | 0     | stop, return,revert                                          |
| Gbase    | 2     | address, origin,caller,callvalue,calldatasize,codesize,gasprice,coinbase,timestamp, number,difficulty,gaslimit,returndatasize,pop,pc,msize,gas |
| Gverylow | 3     | add, sub,not,lt,gt,slt,sgt,eq,iszero,and,or,xor,byte,calldataload,mload,store,mstore8,push*,dup*,swap* |
| Glow     | 5     | mul,div,sdiv,mod,smod,signextend                             |
| Gmid     | 8     | added,mulmod,jump                                            |
| Ghigh    | 10    | jumpier                                                      |
| Gextcode | 700   | extcodesize                                                  |



1. **区分临时存储**（Memory，存在于VM的每个实例中，并在VM执行结束后消失）**和永久存储**（Storage，存在于区块链状态层）；

##  Reference

- [以太坊虚拟机EVM执行原理](http://www.jouypub.com/2018/e7837187669426cba873450586b4a368/)

- [以太坊黄皮书精简解读](http://www.yaofeiliang.com/%E5%8C%BA%E5%9D%97%E9%93%BE/%E4%BB%A5%E5%A4%AA%E5%9D%8A%E9%BB%84%E7%9A%AE%E4%B9%A6%E7%B2%BE%E7%AE%80%E8%A7%A3%E8%AF%BB/)

