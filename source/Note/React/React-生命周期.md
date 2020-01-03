##  生命周期
<html>
<!--
<img src="https://user-images.githubusercontent.com/4705237/43461188-70938bfa-9505-11e8-9676-381282f65908.png"/>
-->
<img src="https://cloud.githubusercontent.com/assets/12592949/24903814/1b2ff98c-1ee1-11e7-9f5a-59eb84171b53.png"/>
</html>

###  Mounting(挂载)
下面这些方法将会在 component 实例被创建和插入到DOM后调用。

1.  `constructor()`  
构造函数，和java class的构造函数一样，用于初始化这个组件的一些状态和操作，如果你是通过继承React.Component子类来创建React的组件的，那么你应当首先调用`super(props)` 初始化父类。
2.  `componentWillMount()`：  
在组件挂载（mount） 之前被调用。因为它是在`render()`方法之前被调用。在该方法中进行同步 setState 不会导致重绘。  
**是否可以使用`setState()`: 可以**
3. `render()`
4. `componentDidMount() `   
该方法在整个React生命周期中只会被调用一次
`componentDidMount()` 在组件挂载之后立即执行。适用于：
   -  需要初始化 DOM 节点的操作
   -   AJAX 请求  
     
   在该钩子函数里面，可以使用 setState()，但是会触发重新渲染（re-render）  
  **是否可以使用`setState()`: 可以**
  
###  Updating 

props 或者 state 的变化都会导致更新。下面这些方法会在 component 重新渲染时调用。

1.  `componentWillReceiveProps()`  
该钩子函数将会在已挂载组件（mounted component）接收到新的 props 之前调用。适用于:   

    -  更新 state的值（比如重置）
    -  比较 this.props 和 nextProps  
   
    即使 Props 没有发生变化，React 也有可能会调用该钩子函数。真正处理 Props 的变化时，需要比较当前 props 和nextProps.出现这种情况的场景：当父组件导致了该组件的 re-render 时，就会出现上述的情况。      
**是否可以使用`setState()`: 可以**
2.  `shouldComponentUpdate()`  
 当组件接收到新的 Props 或者 state时，要进行 rendering之前会调用 `shouldComponentUpdate()`。该钩子函数用于告诉 React 组件是否需要重新渲染.  
  `shouldComponentUpdate() `默认返回 true。  
  `shouldComponentUpdate() `在两种情况下不会被调用：
    -  初始化渲染
    -  使用了 forceUpdate() 情况下  
  
    但是当 `shouldComponentUpdate()` 返回 `false`的时候，此时 `state` 发生改变，并不能阻止 child component 进行重新渲染。
但是一旦 `shouldComponentUpdate() `返回 `false`，这就意味着 `componentWillUpdate()`、 `render()` 和 `componentDidUpdate()`将不再执行。
 
3. `componentWillUpdate()`  
state or props 更新后re-render之前调用。  
不能在这里调用 `setState`，如果需要设置 state，应该在 `componentWillReceiveProps()` 中调用 `setState()`.  
**是否可以使用`setState()`: 不可以**

4. `render()`
5. `componentDidUpdate()`  
在组件更新之后马上调用。在该钩子函数内，你可以：
   -  操作 DOM
   -  发起网络请求
  
     **是否可以使用`setState()`: 可以**


### Unmounting

1.  `componentWillUnmount()`  
在组件卸载和销毁前调用。在该钩子函数内可以做一些清除工作，比如： 

    -  取消定时器
    -  取消网络请求
    -  解绑 DOM 事件   

    **是否可以使用`setState()`: 不可以**


上述的过程便是 React Component 的生命周期执行顺序，依次从上至下执行。

### 总结
以上讲的这些生命周期都有自己存在的意义，但在React使用过程中我们最常用到的生命周期函数是如下几个:
- constructor: 初始化状态，进行函数绑定
- componentDidMount: 进行DOM操作，进行异步调用初始化页面
- componentWillReceiveProps: 根据props更新状态
- componentWillUnmount: 清理组件定时器，网络请求或者相关订阅等

参考如下：  
[React 组件生命周期 #2](https://github.com/superman66/front-end-blog/issues/2)  
[React生命周期管理 #6](https://github.com/frontend9/fe9-library/issues/6)  
[React.js 资料和教程 #12
](https://github.com/thoughtbit/it-note/issues/12)  
[React源码系列(一): 总结看源码心得及方法感受 #1
](https://github.com/jsonz1993/react-source-learn/issues/1)

