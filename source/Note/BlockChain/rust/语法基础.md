## 实例声明

### 变量

- 不可变变量 `let`   ： 代码可读性强；每次需要创建实例，开销较大；
- 可变变量  `let mut` ：复用变量/地址空间；

### 常量

- 声明方式 `const` ：不允许用`mut`；必须注明值的类型；常量只能被设置为常量表达式；

  `const MAX_POINTS: u32 = 100_000;`

```rust
let mut guess = String::new();
// 创建了一个可变变量，当前它绑定到一个新的 String 空实例上
```

`::new` 那一行的 `::` 语法表明 `new` 是 `String` 类型的一个 **关联函数**（*associated function*）。关联函数是针对类型实现的，在这个例子中是 `String`，而不是 `String` 的某个特定实例。一些语言中把它称为 **静态方法**（*static method*）。

`new` 函数创建了一个新的空字符串（String类的实例），很多类型上有 `new` 函数



## 数据类型

### 标量（scalar）



### 复合（compound）

#### 元组（tuple）

- 元组长度固定：一旦声明，其长度不会增大或缩小。

  ```rust
  fn main() {
      //创建了一个包含多个类型元素的元组，并绑定到 tup 变量上。
      let tup = (500, 6.4, 1);
  
      // 接着使用了 let 和一个模式将 tup 分成了三个不同的变量，x、y 和 z。这叫做 解构（destructuring）
      let (x, y, z) = tup;
  
      println!("The value of y is: {}", y);
      
      let tuple: (i32, f64, u8) = (500, 6.4, 1);
  
      // 也可以使用点号（.）后跟值的索引来直接访问它们
      println!("The value of x is: {}", tuple.0);
  }
  ```

  

#### 数组（array）

- 数组固定长度：一旦声明，它们的长度不能增长或缩小。

  ```rust
  fn main() {
      // [元素类型; 元素数量] i32: 标量类型； 5个元素
      let a: [i32; 5] = [1, 2, 3, 4, 5];
      
      // 数组是一整块分配在栈上的内存。可以使用索引来访问数组的元素
      let first = a[0];
      println!("first = {} ", first);
  }
  ```

  

## 函数调用

- 每个参数需要注明类型， 返回值用 `->` 表示

  ```rust
  fn main() {
      let x = plus_one(5);
      println!("The value of x is: {}", x);
  }
  
  fn plus_one(x: i32) -> i32 {
      // return x + 1; 显式的 x + 1
      x + 1
      // x + 1；会报错，相当于执行 return 空
  }
  
  ```

  

## 循环控制

- Rust 有三种循环：`loop`、`while` 和 `for`

  ```rust
  fn main() {
      let mut a: [i32; 4] = [0;4];
      let mut i: i32  = 1; let mut count = 0;
  
      // result 表达式：会返回 loop 过程中的返回值 
      let result = loop {
          if i > 10 {
              break;
          }
          i += i; a[count] = i; count += 1;
      };
      result;   // 执行刚刚的代码块
      
      // while 循环
      while i < 100 {
          i += i;
      }
      println!("i is {}", i);
  
      // for 循环遍历 ： 
      for element in a.iter() {
          println!("iter value is: {}", element);
      }
      
      // 循环遍历 rev: 反转 range
      for number in (1..4).rev() {
          println!("rev  {}!", number);
      }
  }
  ```
  


