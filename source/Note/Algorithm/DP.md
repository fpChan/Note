```go
/* 状态：持有，未持有
   来源：
      持有 --卖出--> 未持有
      持有 --不动--> 持有
      未持有 --买入--> 持有
      未持有 --不动--> 未持有
      
   收益：只要考虑当天买和之前买哪个收益更高，当天卖和之前卖哪个收益更高。
   两个公式
  -  计算买入的成本更低,当天买和之前买哪个成本更低
      buy = min(buy, prices[i])
  -  计算卖出的收益更高，当天卖和之前卖哪个收益更高
      sell = max(sell, prices[i]- buy)
   
*/

func maxProfit(prices []int) int {
    if len(prices) <= 0 { return 0 }
    var buy = prices[0]
    var sell = 0
    for i:= 0; i<len(prices); i++ {
        buy = getMin(buy, prices[i])
        sell = getMax(sell, prices[i] -buy)
    }   
    return sell
}

func getMin(a,b int) int {
    if a < b {
        return a
    }
    return b
}

func getMax(a,b int) int {
    if a > b {
        return a
    }
    return b
}
```