# Solidity系列之基础

## 小知识

- 合约地址是通过 调用地址 + 当前nonce 计算出来的，所以合约地址是可以被提前预估的

  ```go
  func CreateAddress(b common.Address, nonce uint64) common.Address {
  	data, _ := rlp.EncodeToBytes([]interface{}{b, nonce})
  	return common.BytesToAddress(Keccak256(data)[12:])
  }
  ```

  

## 不常见语法

## 习惯

- 变量命名以下划线开始， 以区别全局变量。
- 私有函数的名字用下划线起始

## 函数修饰符

#### 可见修饰符

由于 Solidity 有两种函数调用（内部调用不会产生实际的 EVM 调用或称为“消息调用”，而外部调用则会产生一个 EVM 调用）， 函数和状态变量有四种可见性类型。 函数可以指定为 `external` ，`public` ，`internal` 或者 `private`。 对于状态变量，不能设置为 `external` ，默认是 `internal` 。

- `external`  外部函数作为合约接口的一部分，意味着我们可以从其他合约和交易中调用。 一个外部函数 `f` 不能从内部调用（即 `f` 不起作用，但 `this.f()` 可以）。 当收到大量数据的时候，外部函数有时候会更有效率，因为数据不会从calldata复制到内存.

- `public`   函数是合约接口的一部分，可以在内部或通过消息调用。对于 public 状态变量， 会自动生成一个 getter 函数。

- `internal`   这些函数和状态变量只能是内部访问（即从当前合约内部或从它派生的合约访问）。

- `private`   函数和状态变量仅在当前定义它们的合约中使用，并且不能被派生合约使用。


#### 状态修饰符

- `modifier`   修饰符跟函数很类似，不过是用来修饰其他已有函数用的， 在其他语句执行前，为它检查下先验条件。关键字`modifier` 告诉编译器，这是个`modifier(修饰符)`，而不是个`function(函数)`。它不能像函数那样被直接调用，只能被添加到函数定义的末尾，用以改变函数的行为。

  ```js
  modifier onlyOwner() {
    require(msg.sender == owner);
    _; //修饰符的最后一行为 _;，表示修饰符调用结束后返回，并执行调用函数余下的部分
  }
  
  contract MyContract is Ownable {
  	event LaughManiacally(string laughter);
  	
    function likeABoss() external onlyOwner {
      LaughManiacally("Muahahahaha");
    }
  }
  ```

  > 注意 `likeABoss` 函数上的 `onlyOwner` 修饰符。 当你调用 `likeABoss` 时，**首先执行** `onlyOwner` 中的代码， 执行到 `onlyOwner` 中的 `_;` 语句时，程序再返回并执行 `likeABoss` 中的代码。
  >
  > 可见，尽管函数修饰符也可以应用到各种场合，但最常见的还是放在函数执行之前添加快速的 `require`检查。

- `view`   意味着它只能读取数据不能更改数据

  ```js
  string greeting = "What's up dog";
  function sayHello() public returns (string) {
    return greeting;
  }
  ```

- `pure`  这个函数甚至都不访问应用里的数据. 返回值完全取决于它的输入参数.

  ```js
  function _multiply(uint a, uint b) private pure returns (uint) {
    return a * b;
  }
  ```

- `payable`  修饰符



## 计算

- 加法: `x + y`
- 减法: `x - y`,
- 乘法: `x * y`
- 除法: `x / y`
- 取模 / 求余: `x % y` *(例如, `13 % 5` 余 `3`, 因为13除以5，余3)*
-  乘方操作 (如：x 的 y次方） // 例如：`uint x = 5 ** 2; // equal to 5^2 = 25`





## 预定义的全局变量和函数

当合约在EVM中执行时，它可以访问一组有限的全局对象，包括block、msg和tx对象。另外，以太坊把一些EVM字节码通过预定义函数的方式对外提供。

- **区块和交易对象属性**

   **Block 的数据要有安全性考虑，不能盲目使用，因为其数据取决于矿工如何打包交易，出块**

  - **`blockhash(uint blockNumber) returns (bytes32)`**: 指定区块的哈希值，**仅限于当前区块之前不超过256个区块，否则返回0**

  - **`block.chainid` (`uint`)**:  current chain id

  - **`block.coinbase` (`address payable`)**:  当前区块的矿工地址

  - **`block.difficulty` (`uint`)**: 当前区块工作量证明的难度

  - **`block.gaslimit` (`uint`)**: current block gaslimit

  - **`block.number` (`uint`)**: current block number

  - **`block.timestamp` (`uint`)**: current block timestamp as seconds since unix epoch，由矿工写入的当前区块的时间戳。

  - **`gasleft() returns (uint256)`**: remaining gas

  - **`msg.data` (`bytes calldata`)**: complete calldata，调用合约时传入的数据。

  - **`msg.sender` (`address`)**: sender of the message (current call)

  - **`msg.sig` (`bytes4`)**: first four bytes of the calldata (i.e. function identifier)

  - **`msg.value` (`uint`)**: number of **wei** sent with the message

  - **`tx.gasprice` (`uint`)**: gas price of the transaction

  - **`tx.origin` (`address`)**: sender of the transaction (**full call chain**)

    **此处要有安全性考虑，使用 tx.origin 是调用链路交易的发起者，不能盲目使用**

    

- **计算和加密方法**

  - **`addmod(uint x, uint y, uint k) returns (uint)`**  计算   `(x + y) % k`

  - **`mulmod(uint x, uint y, uint k) returns (uint)`**  计算  `(x * y) % k` 

  - **`keccak256(bytes memory) returns (bytes32)`**    对 数据做 **Keccak-256 hash**

  - **`sha256(bytes memory) returns (bytes32)`**          对 数据做 **sha256 hash**

  - **`ripemd160(bytes memory) returns (bytes20)`**     对 数据做 **RIPEMD-160 hash**

  - **`ecrecover(bytes32 hash, uint8 v, bytes32 r, bytes32 s) returns (address)`**

    ecrecover 通过签名和 数据hash 可以复原 签名的地址，**如果还原出错，返回全0地址** 

- **地址对象**

  - **`<address>.balance` (`uint256`)**      balance of the Address in Wei

  - **`<address>.code` (`bytes memory`)**     code at the [Address](https://docs.soliditylang.org/en/v0.8.6/types.html#address) (can be empty)，指的是合约地址

  - **`<address>.codehash` (`bytes32`)**   the codehash of the [Address](https://docs.soliditylang.org/en/v0.8.6/types.html#address)  1

  - **`<address payable>.transfer(uint256 amount)`** 

    send given amount of Wei to [Address](https://docs.soliditylang.org/en/v0.8.6/types.html#address), reverts on failure, forwards 2300 gas stipend, not adjustable

  - **`<address>.call(bytes memory) returns (bool, bytes memory)`**

    一种底层CALL函数，可以构建一个包含自定义数据的调用，出错时会返回false。警告：这不是一种安全的调用，调用接收方可以无意或有意地耗尽你的gas，导致合约因为00G异常而停止，总是要检查call的返回值。

    **此处要有安全性考虑，使用 transfer 是其默认2300 gas，执行 fallback 函数 有限，但 call 会默认调用全部 gas**

  - **`<address>.delegatecall(bytes memory) returns (bool, bytes memory)`**

    底层 `DELEGATECALL` with the given payload, returns success condition and return data, forwards all available gas, adjustable

  - **`<address>.staticcall(bytes memory) returns (bool, bytes memory)`**

    issue low-level `STATICCALL` with the given payload, returns success condition and return data, forwards all available gas, adjustable

- **合约相关**
  - **`this`** (current contract’s type)  当前合约，**可以转为 Address 类型**

  - **`selfdestruct(address payable recipient)`**

    销毁当前合约，将其资金发送到给定地址并结束执行。请注意，selfdestruct 有一些继承自 EVM 的特性：

    - recipient 如果是个合约，**接收合约的接收函数不会执行**。

      **此处要有安全性考虑， recipient 合约必须接受 eth，合约余额强制增加，并且不执行 fallback 函数**

    - 合约仅在交易结束时才真正被销毁，而 revert 可能会“撤消”销毁。

    **`selfdestruct` 是唯一一个能在单个区块中变更无限个状态对象的操作码**

    其他所有的操作码都只能操作账户中的单个值或者存储树上的单个 key，所以它们能变更多少固定大小的对象是有限制的（通常，调用一个操作码只能变更一个对象）。但是，SELFDESTRUCT 可以删除整棵存储树。









