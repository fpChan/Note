# 从一起“盗币”事件看以太坊存储 hash 碰撞问题

2018-11-09

**Author : Kai Song(exp-sky)、hearmen、salt、sekaiwu of Tencent Security Xuanwu Lab**

## “盗币”

十一月六日，我们观察到以太坊上出现了这样一份[合约](https://etherscan.io/address/0x5170a14aa36245a8a9698f23444045bdc4522e0a#code)，经调查发现是某区块链安全厂商发布的一份让大家来“盗币”的合约。



```sol
pragma solidity ^0.4.21;
contract DVPgame {
    ERC20 public token;
    uint256[] map;
    using SafeERC20 for ERC20;
    using SafeMath for uint256;
    constructor(address addr) payable{
        token = ERC20(addr);
    }
    function (){
        if(map.length>=uint256(msg.sender)){
            require(map[uint256(msg.sender)]!=1);
        }
        if(token.balanceOf(this)==0){
            //airdrop is over
            selfdestruct(msg.sender);
        }else{
            token.safeTransfer(msg.sender,100);

            if (map.length <= uint256(msg.sender)) {
                map.length = uint256(msg.sender) + 1;
            }
            map[uint256(msg.sender)] = 1;  

        }
    }
    //Guess the value(param:x) of the keccak256 value modulo 10000 of the future block (param:blockNum)
    function guess(uint256 x,uint256 blockNum) public payable {
        require(msg.value == 0.001 ether || token.allowance(msg.sender,address(this))>=1*(10**18));
        require(blockNum>block.number);
        if(token.allowance(msg.sender,address(this))>0){
            token.safeTransferFrom(msg.sender,address(this),1*(10**18));
        }
        if (map.length <= uint256(msg.sender)+x) {
            map.length = uint256(msg.sender)+x + 1;
        }

        map[uint256(msg.sender)+x] = blockNum;
    }
    //Run a lottery
    function lottery(uint256 x) public {
        require(map[uint256(msg.sender)+x]!=0);
        require(block.number > map[uint256(msg.sender)+x]);
        require(block.blockhash(map[uint256(msg.sender)+x])!=0);
        uint256 answer = uint256(keccak256(block.blockhash(map[uint256(msg.sender)+x])))%10000;
        if (x == answer) {
            token.safeTransfer(msg.sender,token.balanceOf(address(this)));
            selfdestruct(msg.sender);
        }
    }
}
```

经过观察之后，我们在这个合约中，发现了我们之前研究的一个 EVM 存储的安全问题，即 EVM 存储中的 hash 碰撞问题。

首先，针对上面的合约，如果构造出 `x == uint256(keccak256(block.blockhash(map[uint256(msg.sender)+x])))%10000` 即可在 `lottery` 方法中获取到该合约中的以太币，但是这个 `x` 的值，只能通过不断的猜测去得到，并且概率微乎其微。

然后，我们发现在合约的 fallback 函数中，也存在一个 `selfdestruct` 函数可以帮助我们完成“盗币”任务，但是要求本合约地址在 `token` 合约中的余额为 0。

根据我们之前对于 EVM 存储的分析，我们发现在 `guess` 函数中存在对 `map` 类型数据任意偏移进行赋值 `map[uint256(msg.sender)+x] = blockNum;`，由于在 EVM 中，`map` 类型中数据存储的地址计算方式为 `address(map_data) = sha(key,slot)+offset`，这就造成了一个任意地址写的问题，如果我们能够覆盖到`token` 变量，就能向 `token` 写入我们构造的合约，保证 DVPgame 合约在我们构造合约中的余额为 0，这样就能执行 DVPgame 合约的 `selfdestruct` 函数完成“盗币”。

`token` 变量的地址为0，溢出之后可以达到这个值，即我们需要构造 `sha(msg.sender,slot)+x==2**256(溢出为0)`即可。

## 深入分析

其实早在六月底的时候，经过对 ETH 以及其运行时环境 EVM 的初步研究，我们已经在合约层面和虚拟机层面分别发现了一些问题，其中变量覆盖以及Hash 碰撞问题是非常典型的两个例子。

### 变量覆盖

在某些合约中，我们发现在函数内部对 struct 类型的临时变量进行修改，会在某些情况下覆盖已有的全局变量。

```
pragma solidity ^0.4.23; 
contract Locked {
    bool public unlocked = false;    
    struct NameRecord { 
        bytes32 name;
        address mappedAddress;
    }
    mapping(address => NameRecord) public registeredNameRecord; 
    mapping(bytes32 => address) public resolve;
    function register(bytes32 _name, address _mappedAddress) public {
        NameRecord newRecord;
        newRecord.name = _name;
        newRecord.mappedAddress = _mappedAddress; 
        resolve[_name] = _mappedAddress;
        registeredNameRecord[msg.sender] = newRecord; 
        require(unlocked); 
    }
}
```

合约的源码如上面所示，在正常情况下，由于合约并没有提供修改 unlocked 的接口，因此不太可能达到修改它的目的。但是实际上我们在测试中发现，只要调用合约的 register 方法就可以修改 unlocked。

### Hash 碰撞

经过对 EVM 的存储结构分析，我们发现 EVM 的设计思路中，在其存储某些复杂变量时可能发生潜在的 hash 碰撞，覆盖已有变量，产生不可预知的问题。

```
pragma solidity ^0.4.23; 

contract Project
{
    mapping(address => uint) public balances; // records who registered names 
    mapping(bytes32 => address) public resolve; // resolves hashes to addresses

    uint[] stateVar;

    function Resolve() returns (bytes32){
        balances[msg.sender] = 10000000;   
        return sha3(bytes32(msg.sender),bytes32(0));
    }

    function Resize(uint i){
        stateVar.length = i;
    }

    function Rewrite(uint i){
        stateVar[i] = 0x10adbeef; 
    }

}
```

上面的代码就存在类似的 hash 碰撞问题。查看合约源代码可以看到 `balances` 字段只能通过 `Reslove` 接口进行访问，正常情况下 `balance` 中存放的值是无法被修改的。但是在这个合约中，调用函数 `Rewrite` 对 `stateVar` 进行操作时有可能覆盖掉 `balances` 中的数据

### 背景分析

在 EVM 中存储有三种方式，分别是 memory、storage 以及 stack。

1. memory: 内存，生命周期仅为整个方法执行期间，函数调用后回收，因为仅保存临时变量，故GAS开销很小
2. storage: 永久储存在区块链中，由于会永久保存合约状态变量，故GAS开销也最大
3. stack: 存放部分局部值类型变量，几乎免费使用的内存，但有数量限制

首先我们分析一下各种对象结构在 EVM 中的存储和访问情况

#### Map

首先分析 map 的存储，

```
struct NameRecord { 
    bytes32 name; 
    address mappedAddress;
}
mapping(bytes32 => address) public resolve; 
function register(bytes32 _name, address _mappedAddress) public {
    NameRecord newRecord;
    newRecord.name = _name;
    newRecord.mappedAddress = _mappedAddress; 
    resolve[_name] = _mappedAddress;
}
```

我们在调试 storage 中 map 结构时发现，map 中数据的存储地址其实是 map.key 以及 map 所在位置 map_slot 二者共同的 hash 值，这个值是一个 uint256。即

```
address(map_data) = sha(key,slot)
```

并且我们同时发现，如果 map 中存储的数据是一个结构体，则会将结构体中的成员分别依次顺序存入 storage 中，存储的位置为 `sha(key,slot) + offset`，即是直接将成员在结构体中的偏移与之前计算的 hash 值相加作为存储位置。

这种 `hash + offset` 的 struct 存储方式会直接导致 sha3 算法的 hash 失去意义，在某些情况下产生 `sha(key1,slot) + offset == sha(key2,slot)` ，即 hash 碰撞。

#### Array

接下来我们看一下 Array 的情况

调试中发现全局变量的一个定长 Array 是按照 index 顺序排列在 storage 中的。

如果我们使用 new 关键字申请一个变长数组，查看其运行时存储情况

```
function GetSome() returns(uint){
    stateVar = new uint[](2);
    stateVar[1] = 0x10adbeef;
    //stateVar = [1,2,4,5,6]; // 这种方式和 new 是一样的
    return stateVar[1];
}
```

调试中发现如果是一个变长数组，数组成员的存储位置就是根据 hash 值来选定的了, 数组的存储位置为 `sha3(address(array_object))+index`。数组本身的 slot 中所存放的只是数组的长度而已，这样也就很好理解为什么存放在 storage 中的变长数组可以通过调整 length 属性来自增。

变长数组仍依照 hash + offset 的方式存储。也有可能出现 hash 碰撞的问题。

#### Array + Struct

如果数组和结构体组合起来，那么数据在 storage 中的索引将如何确定呢

```
struct Person {
    address[] addr;
    uint funds;
}    
mapping(address => Person) public people;   
function f() {
    Person p;
    p.addr = [0xca35b7d915458ef540ade6068dfe2f44e8fa733c,0x14723a09acff6d2a60dcdf7aa4aff308fddc160c];
    p.funds = 0x10af;

    people[msg.sender] = p;
}
```

Person 类型的对象 p 第一个成员是一个动态数组 addr，存储 p 对象时，首先在 map 中存储动态数组：

```
storage[hash(msg_sender,people_slot)] = storage[p+slot]
```

接着依次存储动态数组内容:

```
storage[hash(hash(msg_sender,people_slot))] = storage[hash(p_slot)]; storage[hash(hash(msg_sender,people_slot))+1] = storage[hash(p_slot)+1];
```

最后存储 funds：

```
storage[hash(msg_sender,people_slot)+1]
```

同理，数组中的结构体存储也是类似。

### 问题分析

#### 变量覆盖

```
pragma solidity ^0.4.23; 
contract Locked {
    bool public unlocked = false;    
    struct NameRecord { 
        bytes32 name;
        address mappedAddress;
    }
    mapping(address => NameRecord) public registeredNameRecord; 
    mapping(bytes32 => address) public resolve;
    function register(bytes32 _name, address _mappedAddress) public {
        NameRecord newRecord;
        newRecord.name = _name;
        newRecord.mappedAddress = _mappedAddress; 
        resolve[_name] = _mappedAddress;
        registeredNameRecord[msg.sender] = newRecord; 
        require(unlocked); 
    }
}
```

本合约中 unlocked 变量存储在 storage 中偏移为1 的位置。而在调试中发现 newRecord 对象在 storage 部分的索引位置也是 0 ，和全局 unlocked 相重叠，因此访问 newRecord 的时候也会顺便修改到 unlocked。

调试中我们发现所有的临时变量都是从 storage 的 0 位置开始存储的，如果我们多设置几个临时变量，会发现在函数开始选定 slot 时，所有的临时变量对应的 slot 值都是 0。

#### 成因分析

我们下载 solidity 编译器的源码进行查看，分析这里出现问题的原因。源码可在[这里](https://github.com/ethereum/solidity) 找到，直接使用 cmake 编译源码即可，[编译教程](http://solidity.readthedocs.io/en/v0.4.24/installing-solidity.html)。 solidity 的源码需要引用 boost 库，如果之前没有安装的话需要先安装 boost。编译的过程不再赘述，最终会生成三个可执行文件 （在 Windows 上的编译会有点问题，依赖的头文件没办法自动加入工程，需要手动添加，并且会还有一些字符表示的问题）

- `solc\solc`
- `lllc\lllc`
- `test\soltest`

`solc` 可以将 sol 源码编译成 EVM 可以运行的 bytecode

调试 Solc ，查看其中对于 struct 作为临时变量时的编译情况

```
contract Project
{
    uint a= 12345678;
    struct Leak{
        uint s1;
    }
    function f(uint i) returns(uint) {
        Leak l;
        return l.s1;
    }

}
```

关键代码调用栈如下

```
>   solc.exe!dev::solidity::ContractCompiler::appendStackVariableInitialisation(const dev::solidity::VariableDeclaration & _variable) Line 951  C++
    solc.exe!dev::solidity::ContractCompiler::visit(const dev::solidity::FunctionDefinition & _function) Line 445   C++
    solc.exe!dev::solidity::FunctionDefinition::accept(dev::solidity::ASTConstVisitor & _visitor) Line 206  C++
    solc.exe!dev::solidity::ContractCompiler::appendMissingFunctions() Line 870 C++
    solc.exe!dev::solidity::ContractCompiler::compileContract(const dev::solidity::ContractDefinition & _contract, const std::map<dev::solidity::ContractDefinition const *,dev::eth::Assembly const *,std::less<dev::solidity::ContractDefinition const *>,std::allocator<std::pair<dev::solidity::ContractDefinition const * const,dev::eth::Assembly const *> > > & _contracts) Line 75  C++
    solc.exe!dev::solidity::Compiler::compileContract(const dev::solidity::ContractDefinition & _contract, const std::map<dev::solidity::ContractDefinition const *,dev::eth::Assembly const *,std::less<dev::solidity::ContractDefinition const *>,std::allocator<std::pair<dev::solidity::ContractDefinition const * const,dev::eth::Assembly const *> > > & _contracts, const std::vector<unsigned char,std::allocator<unsigned char> > & _metadata) Line 39 C++
    solc.exe!dev::solidity::CompilerStack::compileContract(const dev::solidity::ContractDefinition & _contract, std::map<dev::solidity::ContractDefinition const *,dev::eth::Assembly const *,std::less<dev::solidity::ContractDefinition const *>,std::allocator<std::pair<dev::solidity::ContractDefinition const * const,dev::eth::Assembly const *> > > & _compiledContracts) Line 730  C++
    solc.exe!dev::solidity::CompilerStack::compile() Line 309   C++
    solc.exe!dev::solidity::CommandLineInterface::processInput() Line 837   C++
    solc.exe!main(int argc, char * * argv) Line 59  C++
```

关键函数为 `appendStackVariableInitialisation`，可以看到这里调用 `pushZeroValue` 记录临时变量信息，如果函数发现 value 存在于 Storage 中，那么就直接 `PUSH 0`，直接压入 0！！！所有的临时变量都通过这条路径，换而言之，所有的临时变量 slot 都是 0 。

```
void ContractCompiler::appendStackVariableInitialisation(VariableDeclaration const& _variable)
{
    CompilerContext::LocationSetter location(m_context, _variable);
    m_context.addVariable(_variable);
    CompilerUtils(m_context).pushZeroValue(*_variable.annotation().type);
}
```

笔者目前还不能理解这样设计的原因，猜测可能是因为 storage 本身稀疏数组的关系，不便于通过其他额外变量来控制 slot 位置，但是以目前这样的实现，其问题应该更多。

与之相对的全局变量的编译，函数调用栈如下

```
>   solc.exe!dev::solidity::ContractCompiler::initializeStateVariables(const dev::solidity::ContractDefinition & _contract) Line 403    C++
    solc.exe!dev::solidity::ContractCompiler::appendInitAndConstructorCode(const dev::solidity::ContractDefinition & _contract) Line 146    C++
    solc.exe!dev::solidity::ContractCompiler::packIntoContractCreator(const dev::solidity::ContractDefinition & _contract) Line 165 C++
    solc.exe!dev::solidity::ContractCompiler::compileConstructor(const dev::solidity::ContractDefinition & _contract, const std::map<dev::solidity::ContractDefinition const *,dev::eth::Assembly const *,std::less<dev::solidity::ContractDefinition const *>,std::allocator<std::pair<dev::solidity::ContractDefinition const * const,dev::eth::Assembly const *> > > & _contracts) Line 89   C++
    solc.exe!dev::solidity::Compiler::compileContract(const dev::solidity::ContractDefinition & _contract, const std::map<dev::solidity::ContractDefinition const *,dev::eth::Assembly const *,std::less<dev::solidity::ContractDefinition const *>,std::allocator<std::pair<dev::solidity::ContractDefinition const * const,dev::eth::Assembly const *> > > & _contracts, const std::vector<unsigned char,std::allocator<unsigned char> > & _metadata) Line 44 C++
    solc.exe!dev::solidity::CompilerStack::compileContract(const dev::solidity::ContractDefinition & _contract, std::map<dev::solidity::ContractDefinition const *,dev::eth::Assembly const *,std::less<dev::solidity::ContractDefinition const *>,std::allocator<std::pair<dev::solidity::ContractDefinition const * const,dev::eth::Assembly const *> > > & _compiledContracts) Line 730  C++
    solc.exe!dev::solidity::CompilerStack::compile() Line 309   C++
    solc.exe!dev::solidity::CommandLineInterface::processInput() Line 837   C++
    solc.exe!main(int argc, char * * argv) Line 59  C++
```

关键函数为 `StorageItem::StorageItem` ，函数从 `storageLocationOfVariable` 中获取全局变量在 storage 中的 slot

```
StorageItem::StorageItem(CompilerContext& _compilerContext, VariableDeclaration const& _declaration):
    StorageItem(_compilerContext, *_declaration.annotation().type)
{
    auto const& location = m_context.storageLocationOfVariable(_declaration);
    m_context << location.first << u256(location.second);
}
```

#### hash 碰撞

如前文中提到的，使用 struct 和 array 的智能合约存在出现 hash 碰撞的可能。
一般来说 sha3 方法返回的 hash 是不会产生碰撞的，但是无法保证 hash(mem1)+n 不与其他 hash(mem2) 产生冲突。举个例子来说有两个 map

```
struct Account{
    string name；
    uint ID;
    uint amount;
    uint priceLimit;
    uint total;
}

map<address, uint> balances;     // slot 0  
map<string, Account> userTable;    // slot 1
```

在存储 `balances[key1] = value1` 时计算 `sha3(key1,0) = hash1; Storage[hash1] = value1` 。

存储 `userTable[key2] = account` 时计算 `sha3(key2,1) = hash2;` 。

hash1 和 hash2 是不相同的，但是 hash1 和 hash2 很有可能是临近的，相差很小，我们假设其相差 4 。

此时实际存储 `account` 时，会依次将 `Account.name`、`Account.ID`、`Account.amount`、`Account.priceLimit`、`Account.total`存放在 storage 中 hash2、hash2+1、hash2+2、hash2+3、hash2+4 的位置。而 hash2+4 恰恰等于 hash1 ，那么 `Account.total` 的值就会覆盖之前存储在 `balances` 中的内容 `value1`。

不过通过 struct 攻击只是存在理论上可能，在实际中找到相差很小的 sha3 是很难的。但是如果将问题转化到 array 中，就有可能实现真实的攻击。

因为在 array 中，数组的长度由数组对象第一个字节中存储的数据控制，只要这个值足够大，攻击者就可以覆盖到任意差距的 hash 数据。

```
pragma solidity ^0.4.23; 
contract Project
{
    mapping(address => uint) public balances; // records who registered names 
    mapping(bytes32 => address) public resolve; // resolves hashes to addresses

    uint[] stateVar;

    function Resolve() returns (bytes32){
        balances[msg.sender] = 10000000;   // 0x14723a09acff6d2a60dcdf7aa4aff308fddc160c ->  0x51fb309f06bafadda6dd60adbce5b127369a3463545911e6444ab4017280494d 

        return sha3(bytes32(msg.sender),bytes32(0));
    }

    function Resize(uint i){
        stateVar.length = 0x92b6e4f83ec43f4bc9069880e92f6ea53e45d964038b04cc518a923857c1b79c; // 0x405787fa12a823e0f2b7631cc41b3ba8828b3321ca811111fa75cd3aa3bb5ace
    }

    function Rewrite(uint i){
        stateVar[i] = 0x10adbeef; // 0x11a3a8a4f412d6fcb425fd90f8ca757eb40f014189d800d449d4e6c6cec4ee7f = 0x51fb309f06bafadda6dd60adbce5b127369a3463545911e6444ab4017280494d - 0x405787fa12a823e0f2b7631cc41b3ba8828b3321ca811111fa75cd3aa3bb5ace
    }

}
```

当前的 sender 地址为 `0x14723a09acff6d2a60dcdf7aa4aff308fddc160c` , `balance[msg.sender]` 存储的位置为 `0x51fb309f06bafadda6dd60adbce5b127369a3463545911e6444ab4017280494d`。 调用 `Resize` 方法将数组 `stateVar` 的长度修改，数组的存储位置在 `0x405787fa12a823e0f2b7631cc41b3ba8828b3321ca811111fa75cd3aa3bb5ace`。

最后调用合约方法 `Rewrite` 向数组赋值，该操作会覆盖 `balance` 中的内容，将地址为 sender 的值覆盖。

## 实际内存

最后我们来看一下实际内存的管理情况。无论以太坊区块链的上层技术如何高深，内存终归是需要落地的，最终这些数据还是需要存储在实际的物理内存中的。因此我们通过源码，实际分析 storage 部分的存储情况。EVM 的源码在 https://github.com/ethereum/cpp-ethereum

### 流程分析

1、 EVM 的返回值是通过 EVM 传递的，一般的在 Memory 偏移 0x40 的位置保存着返回值地址，这个地址上保存着真实的返回值

2、Storage 在最底层的实现上是一个 STL 实现稀疏数组，将 slot 值作为 key 来存储值

3、在 Storage 中的 Map 和 变长 Array 均是以 hash 值作为最底层稀疏数组的索引来进行的。 其中变长数组的索引方式为 `hash(array_slot) + index` 而 Map 的索引方式为 `hash(map_slot, key)` ，当 Value 为 Struct 时 Struct 成员会分别存储，每个成员的索引为 `hash(map_slot, key) + offset`

### 代码分析

#### Storage

Storage 部分内存是与合约代码共同存储在区块中的内存，因此 storage 内存消耗的 gas 回相对较多，我们通过 SLOAD 指令查看 Storage 在区块上的存储方式

SLOAD 指令在函数 `interpretCases` 中进行处理，当 EVM 解析到 SLOAD 指令后，首先从栈中获取栈顶元素作为 storage 访问的 key，然后调用函数 `getStorage` 进行实际访问

```
case SLOAD:
    evmc_uint256be key = toEvmC(m_SP[0]);
    evmc_uint256be value;
    m_context->fn_table->get_storage(&value, m_context, &m_message->destination, &key);
    m_SPP[0] = fromEvmC(value);


evmc_context_fn_table const fnTable = {
    accountExists,
    getStorage,
    setStorage,
    getBalance,
    getCodeSize,
    copyCode,
    selfdestruct,
    eth::call,
    getTxContext,
    getBlockHash,
    eth::log,
};
```

`getStorage` 函数接收四个参数，第一个参数为返回地址，第二个参数是当前调用的上下文环境，第三个参数是此次交易信息的目的地址即合约地址，第四个参数是 storage 的索引 key

函数首先对 address 进行验证，保证当前的上下文就是处于合约地址的空间内，接着再调用 `env.store` 实际获取数据

```
void getStorage(
    evmc_uint256be* o_result,
    evmc_context* _context,
    evmc_address const* _addr,
    evmc_uint256be const* _key
) noexcept
{
    (void) _addr;
    auto& env = static_cast<ExtVMFace&>(*_context);
    assert(fromEvmC(*_addr) == env.myAddress);
    u256 key = fromEvmC(*_key);
    *o_result = toEvmC(env.store(key));
}


virtual u256 store(u256 _n) override final { return m_s.storage(myAddress, _n); }
```

最终工作来到 `State::storage` 中

```
u256 State::storage(Address const& _id, u256 const& _key) const
{
    if (Account const* a = account(_id))
    {
        auto mit = a->storageOverlay().find(_key);
        if (mit != a->storageOverlay().end())
            return mit->second;

        // Not in the storage cache - go to the DB.
        SecureTrieDB<h256, OverlayDB> memdb(const_cast<OverlayDB*>(&m_db), a->baseRoot());          // promise we won't change the overlay! :)
        string payload = memdb.at(_key);
        u256 ret = payload.size() ? RLP(payload).toInt<u256>() : 0;
        a->setStorageCache(_key, ret);
        return ret;
    }
    else
        return 0;
}
```

函数首先根据 address 获取对应的 Account 对象

```
Account* State::account(Address const& _addr)
{
    auto it = m_cache.find(_addr);   // m_cache 使用 unordered_map 作为存储结构， find 返回 pair<key, value> 迭代器，迭代器 it->frist 表示 key ; it->second 表示 value
    if (it != m_cache.end())
        return &it->second;

    if (m_nonExistingAccountsCache.count(_addr))  // m_nonExistingAccountsCache 用于记录那些在当前环境下不存在的 addr
        return nullptr;

    // Populate basic info.
    string stateBack = m_state.at(_addr);  //  m_state 即为 StateDB ，以 addr 作为 key 获取这个 account 相关的信息，StateDB 中的数据已经格式化成了 string
    if (stateBack.empty())
    {
        m_nonExistingAccountsCache.insert(_addr);
        return nullptr;
    }

    clearCacheIfTooLarge();

    RLP state(stateBack);  // 创建 RLP 对象。交易必须是正确格式化的RLP。”RLP”代表Recursive Length Prefix，它是一种数据格式，用来编码二进制数据嵌套数组。以太坊就是使用RLP格式序列化对象。
    auto i = m_cache.emplace(
        std::piecewise_construct,
        std::forward_as_tuple(_addr),
        std::forward_as_tuple(state[0].toInt<u256>(), state[1].toInt<u256>(), state[2].toHash<h256>(), state[3].toHash<h256>(), Account::Unchanged)
    );  // 把这个 addr 以及其对应的数据加入到 cache 中，使用逐片构造函数
    m_unchangedCacheEntries.push_back(_addr);
    return &i.first->second;  // 返回这个 account
}
```

下面的注释是部分 Account 对象的说明 ,Account 对象用于表示一个以太账户的状态，Account 对象和 addr 通过 Map 存储在 State 对象中。 每一个 Account 账户包含了一个 storage trie 用于索引其在整个 StateDB 中的节点，Account 对于 storage 的操作会首先在 `storageOverlay` 这个 map 上进行，待之后有需要时才会将数据更新到 trie 上

```
/**
 * Models the state of a single Ethereum account.
 * Used to cache a portion of the full Ethereum state. State keeps a mapping of Address's to Accounts.
 *
 * Aside from storing the nonce and balance, the account may also be "dead" (where isAlive() returns false).
 * This allows State to explicitly store the notion of a deleted account in it's cache. kill() can be used
 * for this.
 *
 * For the account's storage, the class operates a cache. baseRoot() specifies the base state of the storage
 * given as the Trie root to be looked up in the state database. Alterations beyond this base are specified
 * in the overlay, stored in this class and retrieved with storageOverlay(). setStorage allows the overlay
 * to be altered.
 *
```

回到 `State::storage` 函数，在获取了 Account 之后查看 Account 的 storageOverlay 中是否有指定 key 的 value ，如果没有就去 DB 中查找，以 `Account->m_storageRoot` 为根，从 `State->m_db` 中获取一个 db 的拷贝。在这个 tire 的拷贝中查找并将其 RLP 格式化之后存在 `m_storageOverlay` 中

可以看到在实际数据同步到区块上之前，EVM 为 storage 和 account 均提供了二级缓存机制用以提高访存的效率：

- storage： 一级缓存->`account->m_storageOverlay`; 二级缓存->`state->m_db`
- account: 一级缓存->`state->m_cache`; 二级缓存->`state->m_state`

同样我们从存储 Storage 的入口点 SSTORE 开始进行分析, 主体函数为 `VM::interpretCases` , SSTORE opcode 最终会访问一个 unordered_map 类型的 hash 表

```
void VM::interpretCases(){
    // .....
    CASE(SSTORE)
    {
        ON_OP();
        if (m_message->flags & EVMC_STATIC)
            throwDisallowedStateChange();

        updateSSGas();
        updateIOGas();

        evmc_uint256be key = toEvmC(m_SP[0]);
        evmc_uint256be value = toEvmC(m_SP[1]);
        m_context->fn_table->set_storage(m_context, &m_message->destination, &key, &value);
    }
    NEXT
    // .....
}

|-
evmc_context_fn_table const fnTable = {
    accountExists,
    getStorage,
    setStorage,
    getBalance,
    getCodeSize,
    copyCode,
    selfdestruct,
    eth::call,
    getTxContext,
    getBlockHash,
    eth::log,
};


void setStorage(
    evmc_context* _context,
    evmc_address const* _addr,
    evmc_uint256be const* _key,
    evmc_uint256be const* _value
) noexcept
{
    (void) _addr;
    auto& env = static_cast<ExtVMFace&>(*_context);
    assert(fromEvmC(*_addr) == env.myAddress);
    u256 index = fromEvmC(*_key);
    u256 value = fromEvmC(*_value);
    if (value == 0 && env.store(index) != 0)                   // If delete
        env.sub.refunds += env.evmSchedule().sstoreRefundGas;  // Increase refund counter

    env.setStore(index, value);    // Interface uses native endianness
}

|-
    void ExtVM::setStore(u256 _n, u256 _v)
    {
        m_s.setStorage(myAddress, _n, _v);
    }

    |-

        void State::setStorage(Address const& _contract, u256 const& _key, u256 const& _value)
        {
            m_changeLog.emplace_back(_contract, _key, storage(_contract, _key));
            m_cache[_contract].setStorage(_key, _value);
        }

        |-

            class Account{
                // ...
                std::unordered_map<u256, u256> m_storageOverlay;
                // ...
                void setStorage(u256 _p, u256 _v) { m_storageOverlay[_p] = _v; changed(); }
                // ...
            }
```

#### memory

依旧从 MSTORE 入手，查看 EVM 中对 memory 的处理

```
CASE(MSTORE)
{
    ON_OP();
    updateMem(toInt63(m_SP[0]) + 32);
    updateIOGas();

    *(h256*)&m_mem[(unsigned)m_SP[0]] = (h256)m_SP[1];
}
NEXT
```

可以看到 memory 只在当前运行环境中有效，并不存储在与 state 相关的任何位置，因此 memory 只在当前这次运行环境内生效，即 Memory 只在一次交易内生效

#### code

code 与 storage 类似，也是与 Account 相关的，因此 code 也会存储在 Account 对应的结构中，一级缓存为 `account->m_codeCache`； 二级缓存存放位置 `state->m_db[codehash]`，

```
void State::setCode(Address const& _address, bytes&& _code)
{
    m_changeLog.emplace_back(_address, code(_address));
    m_cache[_address].setCode(std::move(_code));
}
```

## 总结

虽然 hash 碰撞的问题出现在了一起类似 CTF 的“盗币”比赛中，但是我们也应该重视由于 EVM 存储设计问题而带来的变量覆盖以及 hash 碰撞之类的问题，希望各位智能合约的开发者们在开发中关注代码中的数据存储，避免由于此类问题带来的损失。

```


```

- 12

- 1

  ```
  https://kuboard-k8s.nervos.tech/namespace/michi
  
  eyJhbGciOiJSUzI1NiIsImtpZCI6ImtGMHp3ckZQSkxKUXV5S0FDNVhlMDZvQnpDMUg4UHJPYWNpbmFfcTZ1a3MifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJtaWNoaSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJwaW5nLXRva2VuLXN2dDhmIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6InBpbmciLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJlOGVmYTgyZi00YWJmLTQwMDItOTRhNy1lYWQ3YzMzMWE4NzMiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6bWljaGk6cGluZyJ9.vPInHPnDyUqIxh2qUQ30WQGhVo6Ris9aMFaOK0LQlE25-5gvDjBWO9RlJLj5LKizbY1bz_hg5Pjuwg5NmpIv4Z45VsWnFoW7ETfLddle0paOvzI93WDIFjr8Z9UJWG1-cG3TxViS18MzRffycHL4B3da1h4SS_1nVhkI7g3hd3qMTdzTcLJlo-owGsFUv_vuh2jXp4GnbVTNUHC29TrAK_koxJY2l0er35UOj3WHmuDyp5qskP-AmNFI45PGQvLyFEMo1GEnDhYJtTmDu96ZP-ncXK0ZpmwdeCr__XflIyQqToE2TTE4MXDPyY6yCB73AmfUz9lLR6rg92UIH6d9Kw
  ```

  

