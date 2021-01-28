# Tree





### 验证一棵树是否为二叉搜索树

```go
func isValidBST(root *TreeNode) bool {
    if(root == nil) {return true}
    if(root.Left !=nil && (getRight(root.Left) >= root.Val)) {return false}
    if(root.Right !=nil && (getLeft(root.Right) <= root.Val)) {return false}
    return (isValidBST(root.Left) && isValidBST(root.Right))
}
func getRight(root *TreeNode) int {
    if(root.Right == nil){return root.Val }
    return getRight(root.Right)
} 
func getLeft(root *TreeNode) int {
    if(root.Left == nil){return root.Val }
    return getLeft(root.Left)
} 
```

### 平衡二叉树

```go
//二叉树，其中每个节点的左和右子树的高度相差不超过1。
func isBalanced(root *TreeNode) bool {
    if(root == nil){ return true }
    if(isBalanced(root.Left) && isBalanced(root.Right)){
        return WithBranch(getHeight(root.Left) - getHeight(root.Right)) <=1
    }
    return false
}
func getHeight(root *TreeNode) int{
    if(root == nil) { return 0 }
    l := getHeight(root.Left) +1
    r := getHeight(root.Right) +1
    if(l <= r){return r}
    return l
}

func WithBranch(n int) int {
    if n < 0 {
        return -n
    }
    return n
}
```

