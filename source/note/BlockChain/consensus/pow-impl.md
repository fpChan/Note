# 转载[PoW挖矿算法原理及其在比特币、以太坊中的实现](https://www.lastupdate.net/18355.html)

PoW，全称Proof of Work，即工作量证明，又称挖矿。大部分公有链或虚拟货币，如比特币、以太坊，均基于PoW算法，来实现其共识机制。即根据挖矿贡献的有效工作，来决定货币的分配。

### 比特币区块

比特币区块由区块头和该区块所包含的交易列表组成。区块头大小为80字节，其构成包括：

4字节：版本号
32字节：上一个区块的哈希值
32字节：交易列表的Merkle根哈希值
4字节：当前时间戳
4字节：当前难度值
4字节：随机数Nonce值

此80字节长度的区块头，即为比特币Pow算法的输入字符串。
交易列表附加在区块头之后，其中第一笔交易为矿工获得奖励和手续费的特殊交易。

bitcoin-0.15.1源码中区块头和区块定义：

```c++
class CBlockHeader
{
public:
    int32_t nVersion;					 //版本号
   
    uint256 hashPrevBlock;		 //上一个区块的哈希值

    uint256 hashMerkleRoot;		 //交易列表的Merkle根哈希值

    uint32_t nTime;						 //当前时间戳

    uint32_t nBits;						 //当前挖矿难度，nBits越小难度越大
    
    uint32_t nNonce; 					//随机数Nonce值
    //其它代码略
};
class CBlock : public CBlockHeader
{
public:
    //交易列表
    std::vector<CTransactionRef> vtx;
    //其它代码略
};
//代码位置src/primitives/block.h
```

 

### 比特币Pow算法原理

Pow的过程，即为不断调整Nonce值，对区块头做双重SHA256哈希运算，使得结果满足给定数量前导0的哈希值的过程。
其中前导0的个数，取决于挖矿难度，前导0的个数越多，挖矿难度越大。

具体如下：

1、生成铸币交易，并与其它所有准备打包进区块的交易组成交易列表，生成Merkle根哈希值。
2、将Merkle根哈希值，与区块头其它字段组成区块头，80字节长度的区块头作为Pow算法的输入。
3、不断变更区块头中的随机数Nonce，对变更后的区块头做双重SHA256哈希运算，与当前难度的目标值做比对，如果小于目标难度，即Pow完成。

Pow完成的区块向全网广播，其他节点将验证其是否符合规则，如果验证有效，其他节点将接收此区块，并附加在已有区块链之后。之后将进入下一轮挖矿。

bitcoin-0.15.1源码中Pow算法实现：

```c++
UniValue generateBlocks(std::shared_ptr<CReserveScript> coinbaseScript, int nGenerate, uint64_t nMaxTries, bool keepScript)
{
    static const int nInnerLoopCount = 0x10000;
    int nHeightEnd = 0;
    int nHeight = 0;
    {   // Don't keep cs_main locked
        LOCK(cs_main);
        nHeight = chainActive.Height();
        nHeightEnd = nHeight+nGenerate;
    }
    unsigned int nExtraNonce = 0;
    UniValue blockHashes(UniValue::VARR);
    while (nHeight < nHeightEnd)
    {
        std::unique_ptr<CBlockTemplate> pblocktemplate(BlockAssembler(Params()).CreateNewBlock(coinbaseScript->reserveScript));
        if (!pblocktemplate.get())
            throw JSONRPCError(RPC_INTERNAL_ERROR, "Couldn't create new block");
        CBlock *pblock = &pblocktemplate->block;
        {
            LOCK(cs_main);
            IncrementExtraNonce(pblock, chainActive.Tip(), nExtraNonce);
        }
        //不断变更区块头中的随机数Nonce
        //对变更后的区块头做双重SHA256哈希运算
        //与当前难度的目标值做比对，如果小于目标难度，即Pow完成
        //uint64_t nMaxTries = 1000000;即重试100万次
        while (nMaxTries > 0 && pblock->nNonce < nInnerLoopCount && !CheckProofOfWork(pblock->GetHash(), pblock->nBits, Params().GetConsensus())) {
            ++pblock->nNonce;
            --nMaxTries;
        }
        if (nMaxTries == 0) {
            break;
        }
        if (pblock->nNonce == nInnerLoopCount) {
            continue;
        }
        std::shared_ptr<const CBlock> shared_pblock = std::make_shared<const CBlock>(*pblock);
        if (!ProcessNewBlock(Params(), shared_pblock, true, nullptr))
            throw JSONRPCError(RPC_INTERNAL_ERROR, "ProcessNewBlock, block not accepted");
        ++nHeight;
        blockHashes.push_back(pblock->GetHash().GetHex());
        //mark script as important because it was used at least for one coinbase output if the script came from the wallet
        if (keepScript)
        {
            coinbaseScript->KeepScript();
        }
    }
    return blockHashes;
}
//代码位置src/rpc/mining.cpp
```

另附bitcoin-0.15.1源码中生成铸币交易和创建新块：

```c++
std::unique_ptr<CBlockTemplate> BlockAssembler::CreateNewBlock(const CScript& scriptPubKeyIn, bool fMineWitnessTx)
{
    int64_t nTimeStart = GetTimeMicros();
    resetBlock();
    pblocktemplate.reset(new CBlockTemplate());
    if(!pblocktemplate.get())
        return nullptr;
    pblock = &pblocktemplate->block; // pointer for convenience
    pblock->vtx.emplace_back();
    pblocktemplate->vTxFees.push_back(-1); // updated at end
    pblocktemplate->vTxSigOpsCost.push_back(-1); // updated at end
    LOCK2(cs_main, mempool.cs);
    CBlockIndex* pindexPrev = chainActive.Tip();
    nHeight = pindexPrev->nHeight + 1;
    //版本号
    pblock->nVersion = ComputeBlockVersion(pindexPrev, chainparams.GetConsensus());
    if (chainparams.MineBlocksOnDemand())
        pblock->nVersion = gArgs.GetArg("-blockversion", pblock->nVersion);
    //当前时间戳
    pblock->nTime = GetAdjustedTime();
    const int64_t nMedianTimePast = pindexPrev->GetMedianTimePast();
    nLockTimeCutoff = (STANDARD_LOCKTIME_VERIFY_FLAGS & LOCKTIME_MEDIAN_TIME_PAST)
                       ? nMedianTimePast
                       : pblock->GetBlockTime();
    fIncludeWitness = IsWitnessEnabled(pindexPrev, chainparams.GetConsensus()) && fMineWitnessTx;
    int nPackagesSelected = 0;
    int nDescendantsUpdated = 0;
    addPackageTxs(nPackagesSelected, nDescendantsUpdated);
    int64_t nTime1 = GetTimeMicros();
    nLastBlockTx = nBlockTx;
    nLastBlockWeight = nBlockWeight;
    //创建铸币交易
    CMutableTransaction coinbaseTx;
    coinbaseTx.vin.resize(1);
    coinbaseTx.vin[0].prevout.SetNull();
    coinbaseTx.vout.resize(1);
    //挖矿奖励和手续费
    coinbaseTx.vout[0].scriptPubKey = scriptPubKeyIn;
    coinbaseTx.vout[0].nValue = nFees + GetBlockSubsidy(nHeight, chainparams.GetConsensus());
    coinbaseTx.vin[0].scriptSig = CScript() << nHeight << OP_0;
    //第一笔交易即为矿工获得奖励和手续费的特殊交易
    pblock->vtx[0] = MakeTransactionRef(std::move(coinbaseTx));
    pblocktemplate->vchCoinbaseCommitment = GenerateCoinbaseCommitment(*pblock, pindexPrev, chainparams.GetConsensus());
    pblocktemplate->vTxFees[0] = -nFees;
    LogPrintf("CreateNewBlock(): block weight: %u txs: %u fees: %ld sigops %d\n", GetBlockWeight(*pblock), nBlockTx, nFees, nBlockSigOpsCost);
    //上一个区块的哈希值
    pblock->hashPrevBlock  = pindexPrev->GetBlockHash();
    UpdateTime(pblock, chainparams.GetConsensus(), pindexPrev);
    //当前挖矿难度
    pblock->nBits          = GetNextWorkRequired(pindexPrev, pblock, chainparams.GetConsensus());
    //随机数Nonce值
    pblock->nNonce         = 0;
    pblocktemplate->vTxSigOpsCost[0] = WITNESS_SCALE_FACTOR * GetLegacySigOpCount(*pblock->vtx[0]);
    CValidationState state;
    if (!TestBlockValidity(state, chainparams, *pblock, pindexPrev, false, false)) {
        throw std::runtime_error(strprintf("%s: TestBlockValidity failed: %s", __func__, FormatStateMessage(state)));
    }
    int64_t nTime2 = GetTimeMicros();
    LogPrint(BCLog::BENCH, "CreateNewBlock() packages: %.2fms (%d packages, %d updated descendants), validity: %.2fms (total %.2fms)\n", 0.001 * (nTime1 - nTimeStart), nPackagesSelected, nDescendantsUpdated, 0.001 * (nTime2 - nTime1), 0.001 * (nTime2 - nTimeStart));
    return std::move(pblocktemplate);
}
//代码位置src/miner.cpp
```

 

### 比特币挖矿难度计算

每创建2016个块后将计算新的难度，此后的2016个块使用新的难度。计算步骤如下：

1、找到前2016个块的第一个块，计算生成这2016个块花费的时间。
即最后一个块的时间与第一个块的时间差。时间差不小于3.5天，不大于56天。
2、计算前2016个块的难度总和，即单个块的难度x总时间。
3、计算新的难度，即2016个块的难度总和/14天的秒数，得到每秒的难度值。
4、要求新的难度，难度不低于参数定义的最小难度。

bitcoin-0.15.1源码中计算挖矿难度代码如下：

```c++
//nFirstBlockTime即前2016个块的第一个块的时间戳
unsigned int CalculateNextWorkRequired(const CBlockIndex* pindexLast, int64_t nFirstBlockTime, const Consensus::Params& params)
{
    if (params.fPowNoRetargeting)
        return pindexLast->nBits;
    //计算生成这2016个块花费的时间
    int64_t nActualTimespan = pindexLast->GetBlockTime() - nFirstBlockTime;
    //不小于3.5天
    if (nActualTimespan < params.nPowTargetTimespan/4)
        nActualTimespan = params.nPowTargetTimespan/4;
    //不大于56天
    if (nActualTimespan > params.nPowTargetTimespan*4)
        nActualTimespan = params.nPowTargetTimespan*4;
    // Retarget
    const arith_uint256 bnPowLimit = UintToArith256(params.powLimit);
    arith_uint256 bnNew;
    bnNew.SetCompact(pindexLast->nBits);
    //计算前2016个块的难度总和
    //即单个块的难度*总时间
    bnNew *= nActualTimespan;
    //计算新的难度
    //即2016个块的难度总和/14天的秒数
    bnNew /= params.nPowTargetTimespan;
    //bnNew越小，难度越大
    //bnNew越大，难度越小
    //要求新的难度，难度不低于参数定义的最小难度
    if (bnNew > bnPowLimit)
        bnNew = bnPowLimit;
    return bnNew.GetCompact();
}
//代码位置src/pow.cpp
```

 

### 以太坊区块

以太坊区块由Header和Body两部分组成。

其中Header部分成员如下：
ParentHash，父区块哈希
UncleHash，叔区块哈希，具体为Body中Uncles数组的RLP哈希值。RLP哈希，即某类型对象RLP编码后做SHA3哈希运算。
Coinbase，矿工地址。
Root，StateDB中state Trie根节点RLP哈希值。
TxHash，Block中tx Trie根节点RLP哈希值。
ReceiptHash，Block中Receipt Trie根节点的RLP哈希值。
Difficulty，区块难度，即当前挖矿难度。
Number，区块序号，即父区块Number+1。
GasLimit，区块内所有Gas消耗的理论上限，创建时指定，由父区块GasUsed和GasLimit计算得出。
GasUsed，区块内所有Transaction执行时消耗的Gas总和。
Time，当前时间戳。
Nonce，随机数Nonce值。

有关叔区块：
叔区块，即孤立的块。以太坊成块速度较快，导致产生孤块。
以太坊会给发现孤块的矿工以回报，激励矿工在新块中引用孤块，引用孤块使主链更重。在以太坊中，主链是指最重的链。

有关state Trie、tx Trie和Receipt Trie：
state Trie，所有账户对象可以逐个插入一个Merkle-PatricaTrie(MPT)结构中，形成state Trie。
tx Trie：Block中Transactions中所有tx对象，逐个插入MPT结构中，形成tx Trie。
Receipt Trie：Block中所有Transaction执行后生成Receipt数组，所有Receipt逐个插入MPT结构中，形成Receipt Trie。

Body成员如下：
Transactions，交易列表。
Uncles，引用的叔区块列表。

go-ethereum-1.7.3源码中区块头和区块定义：

```go
type Header struct {
    //父区块哈希
    ParentHash  common.Hash
    //叔区块哈希
    UncleHash   common.Hash
    //矿工地址
    Coinbase    common.Address
    //StateDB中state Trie根节点RLP哈希值
    Root        common.Hash
    //Block中tx Trie根节点RLP哈希值
    TxHash      common.Hash
    //Block中Receipt Trie根节点的RLP哈希值
    ReceiptHash common.Hash
    Bloom       Bloom
    //区块难度
    Difficulty  *big.Int
    //区块序号
    Number      *big.Int
    //区块内所有Gas消耗的理论上限
    GasLimit    *big.Int
    //区块内所有Transaction执行时消耗的Gas总和
    GasUsed     *big.Int
    //当前时间戳
    Time        *big.Int
    Extra       []byte
    MixDigest   common.Hash
    //随机数Nonce值
    Nonce       BlockNonce
}
type Body struct {
    //交易列表
    Transactions []*Transaction
    //引用的叔区块列表
    Uncles       []*Header
}
//代码位置core/types/block.go
```

 

### 以太坊Pow算法原理

以太坊Pow算法可以表示为如下公式：
RAND(h, n) <= M / d

其中RAND()表示一个概念函数，代表一系列的复杂运算。
其中h和n为输入，即区块Header的哈希、以及Header中的Nonce。
M表示一个极大的数，此处使用2^256-1。
d，为区块难度，即Header中的Difficulty。

因此在h和n确定的情况下，d越大，挖矿难度越大，即为Difficulty本义。
即不断变更Nonce，使RAND(h, n)满足RAND(h, n) <= M / d，即完成Pow。

go-ethereum-1.7.3源码中Pow算法实现：

```go
func (ethash *Ethash) mine(block *types.Block, id int, seed uint64, abort chan struct{}, found chan *types.Block) {
    // Extract some data from the header
    var (
        header = block.Header()
        hash   = header.HashNoNonce().Bytes()
        //target，即M / d，即(2^256-1)/Difficulty
        target = new(big.Int).Div(maxUint256, header.Difficulty)
        number  = header.Number.Uint64()
        dataset = ethash.dataset(number)
    )
    // Start generating random nonces until we abort or find a good one
    var (
        attempts = int64(0)
        nonce    = seed
    )
    logger := log.New("miner", id)
    logger.Trace("Started ethash search for new nonces", "seed", seed)
    for {
        select {
        case <-abort:
            // Mining terminated, update stats and abort
            logger.Trace("Ethash nonce search aborted", "attempts", nonce-seed)
            ethash.hashrate.Mark(attempts)
            return
        default:
            // We don't have to update hash rate on every nonce, so update after after 2^X nonces
            attempts++
            if (attempts % (1 << 15)) == 0 {
                ethash.hashrate.Mark(attempts)
                attempts = 0
            }
            //hashimotoFull即RAND(h, n)所代表的一系列的复杂运算
            digest, result := hashimotoFull(dataset, hash, nonce)
            //result满足RAND(h, n)  <=  M / d
            if new(big.Int).SetBytes(result).Cmp(target) <= 0 {
                // Correct nonce found, create a new header with it
                header = types.CopyHeader(header)
                header.Nonce = types.EncodeNonce(nonce)
                header.MixDigest = common.BytesToHash(digest)
                // Seal and return a block (if still needed)
                select {
                case found <- block.WithSeal(header):
                    logger.Trace("Ethash nonce found and reported", "attempts", nonce-seed, "nonce", nonce)
                case <-abort:
                    logger.Trace("Ethash nonce found but discarded", "attempts", nonce-seed, "nonce", nonce)
                }
                return
            }
            //不断变更Nonce
            nonce++
        }
    }
}
//代码位置consensus/ethash/sealer.go
```

 

### 以太坊挖矿难度计算

以太坊每次挖矿均需计算当前区块难度。
按版本不同有三种计算难度的规则，分别为：calcDifficultyByzantium（Byzantium版）、calcDifficultyHomestead（Homestead版）、calcDifficultyFrontier（Frontier版）。此处以calcDifficultyHomestead为例。

计算难度时输入有：
parent_timestamp：父区块时间戳
parent_diff：父区块难度
block_timestamp：当前区块时间戳
block_number：当前区块的序号

当前区块难度计算公式，即：

```
block_diff = parent_diff
+ (parent_diff / 2048 * max(1 - (block_timestamp - parent_timestamp) // 10, -99)
+ 2^((block_number // 100000) - 2)
```

其中//为整数除法运算符，a//b，即先计算a/b，然后取不大于a/b的最大整数。

调整难度的目的，即为使挖矿时间保持在10-19s期间内，如果低于10s增大挖矿难度，如果大于19s将减小难度。另外，计算出的当前区块难度不应低于以太坊创世区块难度，即131072。

go-ethereum-1.7.3源码中计算挖矿难度代码如下：

```go
func calcDifficultyHomestead(time uint64, parent *types.Header) *big.Int {
    // https://github.com/ethereum/EIPs/blob/master/EIPS/eip-2.mediawiki
    // algorithm:
    // diff = (parent_diff +
    //         (parent_diff / 2048 * max(1 - (block_timestamp - parent_timestamp) // 10, -99))
    //        ) + 2^(periodCount - 2)
    bigTime := new(big.Int).SetUint64(time)
    bigParentTime := new(big.Int).Set(parent.Time)
    // holds intermediate values to make the algo easier to read & audit
    x := new(big.Int)
    y := new(big.Int)
    // 1 - (block_timestamp - parent_timestamp) // 10
    x.Sub(bigTime, bigParentTime)
    x.Div(x, big10)
    x.Sub(big1, x)
    // max(1 - (block_timestamp - parent_timestamp) // 10, -99)
    if x.Cmp(bigMinus99) < 0 {
        x.Set(bigMinus99)
    }
    // (parent_diff + parent_diff // 2048 * max(1 - (block_timestamp - parent_timestamp) // 10, -99))
    y.Div(parent.Difficulty, params.DifficultyBoundDivisor)
    x.Mul(y, x)
    x.Add(parent.Difficulty, x)
    // minimum difficulty can ever be (before exponential factor)
    if x.Cmp(params.MinimumDifficulty) < 0 {
        x.Set(params.MinimumDifficulty)
    }
    // for the exponential factor
    periodCount := new(big.Int).Add(parent.Number, big1)
    periodCount.Div(periodCount, expDiffPeriod)
    // the exponential factor, commonly referred to as "the bomb"
    // diff = diff + 2^(periodCount - 2)
    if periodCount.Cmp(big1) > 0 {
        y.Sub(periodCount, big2)
        y.Exp(big2, y, nil)
        x.Add(x, y)
    }
    return x
}
//代码位置consensus/ethash/consensus.go
```

 

### 后记

Pow算法概念简单，即工作端提交难以计算但易于验证的计算结果，其他节点通过验证这个结果来确信工作端完成了相当的工作量。
但其缺陷也很明显：1、随着节点将CPU挖矿升级为GPU、甚至矿机挖矿，节点数和算力已渐渐失衡；2、比特币等网络每秒需完成数百万亿次哈希计算，资源大量浪费。
为此，业内提出了Pow的替代者如PoS权益证明算法，即要求用户拥有一定数量的货币，才有权参与确定下一个合法区块。另外，相对拥有51%算力，购买超过半数以上的货币难度更大，也使得恶意攻击更加困难。



