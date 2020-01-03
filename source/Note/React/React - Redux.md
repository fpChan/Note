## 基本概念和api
### Store
Store就是保存数据的地方，可以看出是一个容器，整个应用就只能有一个store。Redux提供`reateStore()`函数来生成store
```
import {createStore} from 'redux'
const store = createStore(app);
```
### State  
store 某个节点对应的数据集合就是state。可以通过`store.getState()`获得。  
Redux 规定，一个state对应一个View。State相同，则View相同。

### Action
State 的变化会导致 View 的变化。但是用户接触不到State，只能接触到View。所以State的变化必须是View导致的。Action就是View发出的通知，表示State要发生改变了。  
Action是一个对象，其中type属性是必须的，表示Action的名称。其他属性随意。

### Action Creator
用于生成Action 的函数。

### store.dispatch()
store.dispatch()是View发出Actiion 的唯一办法。
```
import {createStore} from 'redux'
const store = createStore(fn);
store.dispatch(addTodo(text))
```
### Reducer
Store 收到Action之后，必须给出一个新的State，这样才能使View发生变化。这种State的计算过程叫做Reducer。  
Reducer 是一个函数，它接受Action和当前的state作为参数，返回一个新的state。  
整个应用的初始状态，可以作为state的默认值。  
Reducer还可以进行拆分，然后通过combineReducers方法，结合成一个大的Reducer。

## Redux工作流程
首先用户发出Action。
```
store.dispatch(action)
```
然后store自动调用Reducer，并且传入两个参数：当前的state 和 收到的Action. Reducer 会返回新的state。
```
let nextState = reducer(previousState, action)
```
State一旦变化，Store就会调用监听函数。Listener可以通过`store.getState()`得到当前状态。

# 第二部分：redux 中间件
## 中间件与异步操作
Redux解决了同步状态更新的问题，但是异步操作却没有解决。  
如果要 **使Reducer在异步操作结束后自动执行**，必须使用中间件。

### applyMiddleware
`createStore()`方法包含了参数`applyMiddleware()`,  
它是Redux的原生方法，作用是 **将所有的中间件组成一个数组，依次执行**

### 异步操作的基本思路
异步操作需要发出三种Action

- 请求发起时的Action
- 请求成功时的Action
- 请求失败时的Action  

所以流程也很清楚：

1. 操作开始时，dispatch action，触发State更新为正在操作状态
2. 操作结束后 再次 dispatch action,获取结果

解决方案：  
写出一个返回函数的 Action Creator，然后使用`redux-thunk`中间件改造`store.dispatch`。
```
import {createStore, applyMiddleware} from 'redux'
import thunk from 'react-thunk'

const store = createStore(
  rootReducer,
  applyMiddleware(thunk)
)

export function fetchPost() {

}
export function requestPost(){}

export function receivePost(){}

export function handleError(err) {

}

export function requstAync() {
  return function(dispatch){
    // 请求发起时 dispatch action
    dispatch(requestPost())
    // 这里的fetchPost 是一个Promise
    return fetchPost()
    .then(response => response.json())
    .then(json =>
     // 请求成功时 dispatch action
      dispatch(receivePost())
    )
    .catch(err =>
     // 请求错误时 dispatch action
      dispatch(handleError(err))
    )
  }
}
```
参考如下：  
[Redux 学习总结笔记 #3](https://github.com/superman66/front-end-blog/issues/3)  
[React 数据流管理架构之 Redux 介绍
](https://github.com/joeyguo/blog/issues/3):