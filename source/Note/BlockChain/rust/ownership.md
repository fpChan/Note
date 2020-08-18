# 变量与数据

## 所有权

### 所有权规则

-  1、rust 中的每个值都有一个被称为**所有者**（owner）的变量

-  2、值在任意时刻有且只有一个所有者

-  3、当**所有者**（变量）离开作用域，这个值会被丢弃



### 内存与分配

-  `String` 类型，为了支持一个可变，可增长的文本片段，需要在堆上分配一块在编译时未知大小的内存来存放内容。这意味着：

   - 必须在运行时向操作系统请求内存。
   - 需要一个当我们处理完 `String` 时将内存返回给操作系统的方法。

- 当变量离开作用域，Rust 为我们调用一个特殊的函数。这个函数叫做 `drop`，在这里 `String` 的作者可以放置释放内存的代码。Rust 在结尾的 `}` 处自动调用 `drop`。

  

#### 变量与数据交互的方式（一）：移动

- Rust 永远也不会自动创建数据的 “深拷贝”。因此，任何 **自动** 的复制可以被认为对运行时性能影响较小。

- `String` 会申请内存资源，复制时涉及到 内存（值）的所有权转移，参见所有权规则 1

  ```rust
  fn move_test(){
      // 像整型这样的在编译时已知大小的类型被整个存储在栈上
      let stack_str = "stack";
      let copy_stack = stack_str;
      println!("{}, hello!, copy {} ", stack_str, copy_stack);
  
      // String 类型被分配到堆上，所以能够存储在编译时未知大小的文本。
      let heap_str = String::from("heap");
      
      // String实例 heap_str 中指向堆存储的指针作废，move_pointer 复制或者说移动刚刚的指针
      // 拷贝指针、长度和容量而不拷贝数据
      let move_pointer = heap_str;
      println!("{0}, hello!; move stack pointer, {0} data no change", move_pointer); 
  }
  ```

#### 变量与数据交互的方式（二）：克隆
  - 会重新生成一个
    ```rust
    fn clone_test(){
        let heap_str = String::from("hello");
        
        // clone 会深度复制 String 中堆上的数据，而不仅仅是栈上的数据
        let heap_copy = heap_str.clone();
        println!("heap_str = {}, copy = {}", heap_str, heap_copy);
    }
    ```

  

#### 只在栈上的数据：拷贝

- 任何简单标量值的组合可以是 `Copy` 的，不需要分配内存或某种形式资源的类型是 `Copy` 的
  - 所有整数类型，比如 `u32`。
  - 布尔类型，`bool`，它的值是 `true` 和 `false`。
  - 所有浮点数类型，比如 `f64`。
  - 字符类型，`char`。
  - 元组，当且仅当其包含的类型也都是 `Copy` 的时候。比如，`(i32, i32)` 是 `Copy` 的，但 `(i32, String)` 就不是。

#### 所有权转移

- 将值赋给另一个变量时移动它。当持有堆中数据值的变量离开作用域时，其值将通过 `drop` 被清理掉，除非数据被移动为另一个变量所有。

- 函数参数可转移所有权：（copy）/（move）。目前来看取决于传递的类型 是标量值还是占据内存资源的值

- 返回值可转移所有权

  ```rust
   // gives_ownership 将返回值move给调用它的函数
  fn gives_ownership() -> String {          
      let some_string = String::from("hello"); // some_string 进入作用域.
      some_string                              // 返回 some_string 并移出给调用的函数
  }
  
  // takes_and_gives_back 将传入字符串并返回该值
  fn takes_and_gives_back(a_string: String) -> String { // a_string 进入作用域
      "change".to_owned()  // 返回并move给调用的函数
  } // a_string 移出作用域并被丢弃。
  
  fn makes_copy(some_integer: i32) { // some_integer 进入作用域
      println!("{}", some_integer);
  } // 这里，some_integer 移出作用域。不会有特殊操作
  
  fn ownership_test() {
      let s1 = gives_ownership();         // gives_ownership 将返回值move 给s1
  
      let s2 = String::from("hello");     // s2 进入作用域
  
      // s2 被move到函数中,它也将返回值移给 s3。
      // 根据规则二: s2已经没有所有权, 不能使用
      let s3 = takes_and_gives_back(s2); 
  
      println!("s1 = {}, s3 = {}",s1, s3);
  
      let x = 5;                      // x 进入作用域
      
      makes_copy(x);                  // x 应该移动函数里，但 i32 是 Copy 的，所以在后面可继续使用 x
  
  } // 根据规则三: 这里, s3 移出作用域并被丢弃。s2 也移出作用域，但已被移走，
    // 所以什么也不会发生。s1 移出作用域并被丢弃
  
  ```



## 引用

### 规则

- 在任意给定时间，**要么** 只能有一个可变引用，**要么** 只能有多个不可变引用。
- 引用必须总是有效的。

### 实例

- 可变引用/

  ```rust
  fn reference_test() {
      let s1 = String::from("hello");
  
      let len = calculate_length(&s1);
      println!("The length of '{}' is {}.", s1, len);
      
      // 在特定作用域中的特定数据只能有一个可变引用。可以通过代码块来变通约束条件
      {
          let r1 = &mut s1;
  
      } // r1 在这里离开了作用域，所以我们完全可以创建一个新的引用
      
      let r2 = &mut s1;
  }
  
  fn calculate_length(s: &String) -> usize { // s 是对 String 的引用; 获取引用作为函数参数称为 借用（borrowing）
      s.len()
  }// 这里，s 离开了作用域。但因为它并不拥有引用值的所有权，所以什么也不会发生
  ```

  