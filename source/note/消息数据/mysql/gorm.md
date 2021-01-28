# gorm

#### 创建连接

```go
 db, err := gorm.Open("mysql", "user:password@/dbname?charset=utf8&parseTime=True&loc=Local")

```

#### 数据模型定义

##### 表名，列名如何对应结构体

在Gorm中，表名是结构体名的复数形式，列名是字段名的蛇形小写。

**即，如果有一个Order表，那么如果你定义的结构体名为：User，gorm会默认表名为orders而不是order。**

```sql
CREATE TABLE `orders` (
  `order_id` varchar(3) NOT NULL,
  `status` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`order_id`),
  KEY `idx_orders_status` (`status`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

那么对应的结构体定义如下：

```go
type Order struct {
	OrderId        string `gorm:"PRIMARY_KEY;type:varchar(3)" json:"orderId"`
	Status         int64  `gorm:"index;" json:"status"` //索引
}
```

如何全局禁用表名复数呢？

可以在创建数据库连接的时候设置如下参数：

```go
// 全局禁用表名复数
db.SingularTable(true) // 如果设置为true,`User`的默认表名为`user`,使用`TableName`设置的表名不受影响
```

这样的话，表名默认即为结构体的首字母小写形式。

#### 生成表

当数据库需要频繁更新结构时,代码与数据库难以保持一致是烦人的问题.而golang的gorm库,有Auto Migration功能,可以根据go里的struct tag自动更新数据库结构, 非常方便。

```
//自动生成表
db.AutoMigrate(&Order{})
```

#### 查询

```go
query := db.Model(Order{}).Where("order_id = ? AND status = ?", order_id, status)
var count int
err := db.Model(&Order{}).Where(&Order{order_id: id, status: status}).Count(&count).Error
```

先用 `db.Model()`选择一个表，再用 `db.Where()`构造查询条件，后面可以使用 `db.Count()`计算数量，如果要获取对象，可以使用 `db.Find(&Likes)`或者只需要查一条记录 `db.First(&Order)`



#### 事务

要在事务中执行一组操作，一般流程如下。

```go
func CreateAnimals(db *gorm.DB) err {
  tx := db.Begin()
  // 注意，一旦你在一个事务中，使用tx作为数据库句柄

  if err := tx.Create(&Animal{Name: "Giraffe"}).Error; err != nil {
     tx.Rollback()
     return err
  }
  // 在事务中做一些数据库操作（从这一点使用'tx'，而不是'db'）
  if err := tx.Create(&Animal{Name: "Lion"}).Error; err != nil {
     tx.Rollback()
     return err
  }

  tx.Commit()
  return nil
}
```





#### 日志

Gorm有内置的日志记录器支持，默认情况下，它会打印发生的错误。

```go
// 启用Logger，显示详细日志
db.LogMode(true)

// 禁用日志记录器，不显示任何日志
db.LogMode(false)

// 调试单个操作，显示此操作的详细日志
db.Debug().Where("name = ?", "xiaoming").First(&User{})
```

#### 参考如下：

[Go orm框架gorm学习](https://www.cnblogs.com/rickiyang/p/11074162.html)