# Bookstore

## 成员

| 学号        | 姓名   | 分工                                                         |
| ----------- | :----- | ------------------------------------------------------------ |
| 10205501460 | 吴陆盟 | 实现并测试前60%功能（使用orm实现项目基本功能）；管理`Github`仓库；测试整个项目 |
| 10205501407 | 李思涵 | 实现并测试搜索接口的图书功能（创建倒排索引、分页显示等）     |
| 10205501420 | 许琪   | 实现并测试买家用户接口的收货功能、卖家用户接口的发货功能和买家主动或超时自动取消订单功能 |

## 关系数据库设计

### ER图![er](D:\Coding_Documents\class_practice\db\pj2\bookstore_CDMS2022\markdown\main.assets\er.png)



### 关系模式

```mermaid
classDiagram
direction BT
class bookstore_book {
   text title
   text author
   text publisher
   text original_title
   text translator
   text pub_year
   integer pages
   integer price
   text currency_unit
   text binding
   text isbn
   text author_intro
   text book_intro
   text content
   text tags
   bytea picture
   tsvector token
   text id
}
class bookstore_new_order {
   text user_id
   text store_id
   text status
   timestamp time
   text order_id
}
class bookstore_new_order_detail {
   integer count
   integer price
   text order_id
   text book_id
}
class bookstore_store {
   text book_info
   integer stock_level
   text store_id
   text book_id
}
class bookstore_user {
   text password
   integer balance
   text token
   text terminal
   text user_id
}
class bookstore_user_store {
   text user_id
   text store_id
}


```

## 项目结构

```bash
│  .gitignore
│  jieba_book.py	分词，创建GIN索引
│  log.txt			git记录
│  README.md		
│  requirements.txt	
│  
├─be				后端
│  │  app.py	
│  │  serve.py		启动后端
│  │  __init__.py
│  │  
│  ├─model			逻辑代码
│  │      
│  └─view			后端接口
│          
├─fe
│  │  conf.py
│  │  conftest.py
│  │  __init__.py
│  │  
│  ├─access
│  │      
│  ├─bench
│  │      
│  └─test			功能性测试
│          
├─markdown
│          
├─script
│      test.sh		生成coverage
│      
└─test_result		测试结果
    │  .coverage
    │  res.txt
    │  
    └─htmlcov
```



## 功能实现

### 数据库相关配置

本项目使用的orm框架为`SQLAlchemy`。在简单的使用场景中，我们只需要利用`sessionmaker()`创建工厂类，再用这个工厂类实例化一个`session`即可。但鉴于本项目是多线程的，并考虑到事务处理，我们通过以下方式实现`session`相关的操作：

```python
# be/model/store.py
# 已省去与session无关的部分

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from contextlib import contextmanager


class Store:

    def __init__(self):

        self.engine = create_engine("postgresql+psycopg2://postgres:123456@localhost:5432/postgres",echo=True)
        self.DBSession = sessionmaker(bind=self.engine)
        
    @contextmanager
    def get_db_session(self):
        try:
            session = scoped_session(self.DBSession)
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.remove()
```

* 使用`scoped_session()`，保证线程安全。

* 使用`@contextmanager`装饰器

  * 考虑到`session`的提交，回收以及回滚的需求，我们利用`@contextmanager`创建一个上下文管理器，帮助我们方便地实现`enter`和`exit`方法。通过`with as`，我们可以获得`yield` 的`session`，然后我们就可以提交该`session`；如果出错了，那就可以回滚；最后，这个`session`就会被回收。具体地，通过以下这个例子阐述：

    ```python
    #卖家买家的余额变动、删除new_order(detail)必须在一个session里，这样可以出错了rollback
    with self.get_session() as session:
    	buyer = session.query(User_model).filter(and_(User_model.user_id==buyer_id,User_model.balance>=total_price)).all()
    	if len(buyer) !=1:
    		return error.error_not_sufficient_funds(order_id)
                
    	buyer = buyer[0]
    	buyer.balance = buyer.balance-total_price
    	session.add(buyer)
    
    	seller = session.query(User_model).filter(User_model.user_id == seller_id).all()
    	if len(seller) !=1:
    		return error.error_non_exist_user_id(seller_id)
                    
    	seller = seller[0]
    	seller.balance = seller.balance+total_price
    	session.add(seller)
    
    	# 支付以后订单不删除，修改状态已支付为未支付
    	order = session.query(NewOrder_model).filter(NewOrder_model.order_id == order_id).all()
    	if len(order) != 1:
    		return error.error_invalid_order_id(order_id)
    
    	order = order[0]
    	order.status = "已支付"
    	session.add(order)
    ```

    该例截取自一段与买家支付功能有关的代码。其中包括三个操作：卖家余额变动、买家余额变动、订单状态变动。出于事务处理的**原子性**的考虑，这三个操作或是全部执行成功，或是全部不执行。通过调用上文被修饰过的函数，我们便可以达到这个目的。

### 用户权限接口

#### 登录

**请求地址：**`POST` `/auth/login`

**Request**

Body:

```
{
    "user_id":"$user name$",
    "password":"$user password$",
    "terminal":"$terminal code$"
}
```

| 变量名   | 类型   | 描述     | 是否可为空 |
| -------- | ------ | -------- | ---------- |
| user_id  | string | 用户名   | N          |
| password | string | 登陆密码 | N          |
| terminal | string | 终端代码 | N          |

**Response**

Status Code:

| 码   | 描述                       |
| ---- | -------------------------- |
| 200  | 登录成功                   |
| 401  | 登录失败，用户名或密码错误 |

Body:

```
{
    "message":"$error message$",
    "token":"$access token$"
}
```

| 变量名  | 类型   | 描述                                                         | 是否可为空   |
| ------- | ------ | ------------------------------------------------------------ | ------------ |
| message | string | 返回错误消息，成功时为"ok"                                   | N            |
| token   | string | 访问token，用户登录后每个需要授权的请求应在headers中传入这个token | 成功时不为空 |

#### 登出

**请求地址：**`POST` `/auth/logout`

**Request**

Headers:

| key   | 类型   | 描述      |
| ----- | ------ | --------- |
| token | string | 访问token |

Body:

```
{
    "user_id":"$user name$"
}
```

| 变量名  | 类型   | 描述   | 是否可为空 |
| ------- | ------ | ------ | ---------- |
| user_id | string | 用户名 | N          |

**Response**

Status Code:

| 码   | 描述                        |
| ---- | --------------------------- |
| 200  | 登出成功                    |
| 401  | 登出失败，用户名或token错误 |

Body:

```
{
    "message":"$error message$"
}
```

| 变量名  | 类型   | 描述                       | 是否可为空 |
| ------- | ------ | -------------------------- | ---------- |
| message | string | 返回错误消息，成功时为"ok" | N          |

#### 注册

**请求地址：**`POST` `/auth/register`

**Request**

Body:

```json
{
    "user_id":"$user name$",    
    "password":"$user password$"
}
```

| 变量名   | 类型   | 描述     | 是否可为空 |
| -------- | ------ | -------- | ---------- |
| user_id  | string | 用户名   | N          |
| password | string | 登陆密码 | N          |

**Response**

Status Code:


| 码   | 描述                 |
| ---- | -------------------- |
| 200  | 注册成功             |
| 5XX  | 注册失败，用户名重复 |

Body:

```
{
    "message":"$error message$"
}
```

| 变量名  | 类型   | 描述                       | 是否可为空 |
| ------- | ------ | -------------------------- | ---------- |
| message | string | 返回错误消息，成功时为"ok" | N          |

#### 注销

**请求地址：**`POST` `/auth/unregister`

**Request**

Body:

```
{
    "user_id":"$user name$",
    "password":"$user password$"
}
```

| 变量名   | 类型   | 描述     | 是否可为空 |
| -------- | ------ | -------- | ---------- |
| user_id  | string | 用户名   | N          |
| password | string | 登陆密码 | N          |

**Response**

Status Code:


| 码   | 描述                               |
| ---- | ---------------------------------- |
| 200  | 注销成功                           |
| 401  | 注销失败，用户名不存在或密码不正确 |


Body:

```
{
    "message":"$error message$"
}
```

| 变量名  | 类型   | 描述                       | 是否可为空 |
| ------- | ------ | -------------------------- | ---------- |
| message | string | 返回错误消息，成功时为"ok" | N          |

#### 修改密码

**请求地址：**`POST` `/auth/password`

**Request**

Body:

```
{
    "user_id":"$user name$",
    "oldPassword":"$old password$",
    "newPassword":"$new password$"
}
```

| 变量名      | 类型   | 描述         | 是否可为空 |
| ----------- | ------ | ------------ | ---------- |
| user_id     | string | 用户名       | N          |
| oldPassword | string | 旧的登陆密码 | N          |
| newPassword | string | 新的登陆密码 | N          |

**Response**

Status Code:

| 码   | 描述         |
| ---- | ------------ |
| 200  | 更改密码成功 |
| 401  | 更改密码失败 |

Body:

```
{
    "message":"$error message$",
}
```

| 变量名  | 类型   | 描述                       | 是否可为空 |
| ------- | ------ | -------------------------- | ---------- |
| message | string | 返回错误消息，成功时为"ok" | N          |

### 买家用户接口

#### 下单

**请求地址：**`POST` `/buyer/new_order`

**Request**

Header:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

Body:

```json
{
  "user_id": "buyer_id",
  "store_id": "store_id",
  "books": [
    {
      "id": "1000067",
      "count": 1
    },
    {
      "id": "1000134",
      "count": 4
    }
  ]
}
```

属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
store_id | string | 商铺ID | N
books | class | 书籍购买列表 | N

books数组：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
id | string | 书籍的ID | N
count | string | 购买数量 | N

**Response**

Status Code:

码 | 描述
--- | ---
200 | 下单成功
5XX | 买家用户ID不存在
5XX | 商铺ID不存在
5XX | 购买的图书不存在
5XX | 商品库存不足

Body:

```json
{
  "order_id": "uuid"
}
```

属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
order_id | string | 订单号，只有返回200时才有效 | N

#### 付款

**请求地址：**`POST` `/buyer/payment`

**Request**

Body:

```json
{
  "user_id": "buyer_id",
  "order_id": "order_id",
  "password": "password"
}
```

属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
order_id | string | 订单ID | N
password | string | 买家用户密码 | N 

**Response**

Status Code:

码 | 描述
--- | ---
200 | 付款成功
5XX | 账户余额不足
5XX | 无效参数
401 | 授权失败 

#### 充值

**请求地址：**`POST` `/buyer/add_funds`

**Request**

Body:

```json
{
  "user_id": "user_id",
  "password": "password",
  "add_value": 10
}
```

属性说明：

key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 买家用户ID | N
password | string | 用户密码 | N
add_value | int | 充值金额，以分为单位 | N


Status Code:

码 | 描述
--- | ---
200 | 充值成功
401 | 授权失败
5XX | 无效参数

#### 收货（附加功能）

> 传入买家id和订单id  
>
> 检查订单是否存在：用order_id查询NewOrder表  
>
> 是否属于该买家：用user_id查询UserStore表  
>
> 检查订单状态：用order_id查询NewOrder表获取status  
>
> 如果订单状态为已发货，则将NewOrder表中该记录的status修改为已收货  
>
> 其他状态不允许修改订单状态为已收货。  

**请求地址：**
POST http://[address]/buyer/received

**Request**

Body:

```json
{"user_id": "$user_id$", "order_id": "$order_id$"}
```

| 变量名   | 类型   | 描述               | 是否可为空 |
| -------- | ------ | ------------------ | ---------- |
| user_id  | string | 买家用户的id       | N          |
| order_id | string | 买家要收货的订单id | N          |

**Response**

Status Code:

| 码   | 描述                                   |
| ---- | -------------------------------------- |
| 200  | 收货成功                               |
| 401  | 权限错误，该订单的买家不是该用户       |
| 518  | 无效订单                               |
| 520  | 不是已发货的订单：未支付/已支付/已收货 |

**test**  

未支付订单/未发货订单/订单id错误/重复收货/买家id错误  

#### **查询历史订单（附加功能）**

> 传入买家id 
>
> 检查该用户是否有订单：用user_id查询NewOrder表获取订单列表信息  
>
> 用查询到的order_id查询NewOrderDetail表获取订单具体信息
>
> 检查查询的detail是否为空，空则返回订单错误  
>
> 将订单和订单具体信息返回。    

**请求地址：**`POST` `/buyer/search_order`

**Request**

Body:

```json
{
    "user_id": "$user_id$"
}
```

| 变量名  | 类型   | 描述         | 是否可为空 |
| ------- | ------ | ------------ | ---------- |
| user_id | string | 买家用户的id | N          |

**Response**

Status Code:  

| 码   | 描述         |
| ---- | ------------ |
| 200  | 查询成功     |
| 518  | 无效订单     |
| 521  | 用户没有订单 |

Body:

```json
{
  "order_list": 
  [{
    "order_id": "$order_id$",
    "store_id": "$store_id$",
    "time": "$time$",
    "status": "$status$",
    "details": 
        [{
          "book_id": "$book_id$",
          "count": "$count$",
          "price": "$price$"
        }]
  }]
}
```

属性说明：

| 变量名         | 类型   | 描述                        | 是否可为空 |
| -------------- | ------ | --------------------------- | ---------- |
| order_id       | string | 订单号，只有返回200时才有效 | N          |
| store_id       | string | 商店号，只有返回200时才有效 | N          |
| time           | string | 订单创建时间                | N          |
| status         | string | 订单状态                    | N          |
| detail         | list   | 存储订单具体信息            | N          |
| detail.book_id | string | 购买的书号                  | N          |
| detail.count   | int    | 购买的数量                  | N          |
| detail.price   | int    | 书的价格                    | N          |

**test**  

买家id错误/订单没有内容

#### 取消订单（附加功能）

**请求地址：**`POST` `/buyer/cancel_order`

**Request**

Body:

```json
{"user_id": "$user_id$", "order_id": "$order_id$"}
```

| 变量名   | 类型   | 描述           | 是否可为空 |
| -------- | ------ | -------------- | ---------- |
| user_id  | string | 买家用户的id   | N          |
| order_id | string | 要取消的订单id | N          |

**Response**

Status Code:  

| 码   | 描述                                       |
| ---- | ------------------------------------------ |
| 200  | 取消成功                                   |
| 518  | 无效订单                                   |
| 513  | 该商店id不存在                             |
| 520  | 该状态不允许取消订单操作，已发货/已收货    |
| 401  | 权限错误                                   |
| 515  | 不存在该book_id                            |
| 514  | 该商店id对应的卖家不存在                   |
| 511  | 该买家id不存在                             |
| 519  | 买家已支付订单，取消订单时卖家的钱不够退回 |

**test**  

未支付/已支付订单取消成功  
已发货/已收货订单取消失败、订单id错误、重复取消、错误买家id、卖家的钱不够扣除  

### 卖家用户接口

#### 创建店铺

**请求地址：**`POST` `/seller/create_store`

**Request**

Headers:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

Body:

```json
{
  "user_id": "$seller id$",
  "store_id": "$store id$"
}
```

key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 卖家用户ID | N
store_id | string | 商铺ID | N

**Response**

Status Code:

码 | 描述
--- | ---
200 | 创建商铺成功
5XX | 商铺ID已存在

#### 添加书籍信息

**请求地址：**`POST` `/seller/add_book`

**Request**

Headers:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

Body:

```json
{
  "user_id": "$seller user id$",
  "store_id": "$store id$",
  "book_info": {
    "tags": [
      "tags1",
      "tags2",
      "tags3",
      "..."
    ],
    "pictures": [
      "$Base 64 encoded bytes array1$",
      "$Base 64 encoded bytes array2$",
      "$Base 64 encoded bytes array3$",
      "..."
    ],
    "id": "$book id$",
    "title": "$book title$",
    "author": "$book author$",
    "publisher": "$book publisher$",
    "original_title": "$original title$",
    "translator": "translater",
    "pub_year": "$pub year$",
    "pages": 10,
    "price": 10,
    "binding": "平装",
    "isbn": "$isbn$",
    "author_intro": "$author introduction$",
    "book_intro": "$book introduction$",
    "content": "$chapter1 ...$"
  },
  "stock_level": 0
}

```

属性说明：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 卖家用户ID | N
store_id | string | 商铺ID | N
book_info | class | 书籍信息 | N
stock_level | int | 初始库存，大于等于0 | N

book_info类：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
id | string | 书籍ID | N
title | string | 书籍题目 | N
author | string | 作者 | Y
publisher | string | 出版社 | Y
original_title | string | 原书题目 | Y
translator | string | 译者 | Y
pub_year | string | 出版年月 | Y
pages | int | 页数 | Y
price | int | 价格(以分为单位) | N
binding | string | 装帧，精状/平装 | Y
isbn | string | ISBN号 | Y
author_intro | string | 作者简介 | Y
book_intro | string | 书籍简介 | Y
content | string | 样章试读 | Y
tags | array | 标签 | Y
pictures | array | 照片 | Y

tags和pictures：

​    tags 中每个数组元素都是string类型 
​    picture 中每个数组元素都是string（base64表示的bytes array）类型

**Response**

Status Code:

码 | 描述
--- | ---
200 | 添加图书信息成功
5XX | 卖家用户ID不存在
5XX | 商铺ID不存在
5XX | 图书ID已存在

#### 添加书籍库存

**请求地址：**`POST` `/seller/add_stock_level`

**Request**

Headers:

key | 类型 | 描述 | 是否可为空
---|---|---|---
token | string | 登录产生的会话标识 | N

Body:

```json
{
  "user_id": "$seller id$",
  "store_id": "$store id$",
  "book_id": "$book id$",
  "add_stock_level": 10
}
```
key | 类型 | 描述 | 是否可为空
---|---|---|---
user_id | string | 卖家用户ID | N
store_id | string | 商铺ID | N
book_id | string | 书籍ID | N
add_stock_level | int | 增加的库存量 | N

**Response**

Status Code:

码 | 描述
--- | :--
200 | 创建商铺成功
5XX | 商铺ID不存在 
5XX | 图书ID不存在 

#### 发货（附加功能）

> 传入卖家id和订单id 
> 
> 检查订单是否存在：用order_id查询NewOrder表
> 
> 是否属于该卖家：用user_id查询UserStore表 
> 
> 检查订单状态：用order_id查询NewOrder表获取status 
> 
> 如果订单状态为已支付，则将NewOrder表中该记录的status修改为已发货 
> 
> 其他状态不允许修改订单状态为已发货。

**请求地址：**`POST` `/seller/delivered`

**Request**

Body:

```json
{
    "user_id":"$user_id$",
    "order_id":"$order_id$"
}
```

| 变量名   | 类型   | 描述               | 是否可为空 |
| -------- | ------ | ------------------ | ---------- |
| user_id  | string | 卖家用户的id       | N          |
| order_id | string | 卖家要发货的订单id | N          |

**Response**

Status Code:

| 码   | 描述                                   |
| ---- | -------------------------------------- |
| 200  | 发货成功                               |
| 401  | 权限错误，该订单的卖家不是该用户       |
| 518  | 无效订单                               |
| 520  | 不是已支付的订单：未支付/已发货/已收货 |

**test**  

order_id错误/未支付订单/重复发货/卖家id错误  

#### 查询名下商店的所有订单（附加功能）

> 传入卖家id和商店id  
> 检查该商店是否有订单，用store_id查询NewOrder表获取订单列表信息    
> 用查询到的order_id查询NewOrderDetail表获取订单具体信息  
> 检查查询的detail是否为空，空则返回订单错误  
> 将订单和订单具体信息返回。  

**请求地址：**  `POST` `/seller/seller_search`

**Request**

Body:

```json
{"user_id": "$seller_id$","store_id": "$store_id$"}
```

| 变量名   | 类型   | 描述           | 是否可为空 |
| -------- | ------ | -------------- | ---------- |
| user_id  | string | 卖家用户的id   | N          |
| store_id | string | 要查询的商店id | N          |

**Response**

Status Code:  

| 码   | 描述         |
| ---- | ------------ |
| 200  | 查询成功     |
| 518  | 无效订单     |
| 523  | 商店没有订单 |

Body:

```json
{
  "order_list": 
  [{
    "order_id": "$order_id$",
    "user_id": "$user_id$",
    "time": "$time$",
    "status": "$status$",
    "details": 
        [{
          "book_id": "$book_id$",
          "count": "$count$",
          "price": "$price$"
        }]
  }]
}
```

属性说明：

| 变量名         | 类型   | 描述                        | 是否可为空 |
| -------------- | ------ | --------------------------- | ---------- |
| order_id       | string | 订单号，只有返回200时才有效 | N          |
| user_id        | string | 买家号，只有返回200时才有效 | N          |
| time           | string | 订单创建时间                | N          |
| status         | string | 订单状态                    | N          |
| detail         | list   | 存储订单具体信息            | N          |
| detail.book_id | string | 购买的书号                  | N          |
| detail.count   | int    | 购买的数量                  | N          |
| detail.price   | int    | 书的价格                    | N          |

**test**  

卖家id错误/订单没有内容  

### 搜索接口

#### 搜索图书（附加功能）

>创建子查询，得到与搜索关键字有关的每本书的标题，和使用 ts_rank 函数计算得到的对应的分数。再创建查询，搜索 book 表中对应子查询的书的标题、作者、出版商、翻译、作者信息、图书信息、关键词，按照分数降序排序，即越符合搜索关键字的越靠前，且图书必须在 store 表有记录且库存须大于0，即搜索范围实际是 bookstore 中有库存的书。对于店铺内搜索，限制 store_id 为输入的店铺名即可。得到所有搜索结果（row），需要判断是否为空，否则返回相应 code and message。以5条结果为1页，计算总页数（pagenum），再另外储存前5条结果为第一页显示的内容（show）以显示在当前页面。最后返回所有所需参数。  

**请求地址** `POST` `/searcher/search`

**Request**

Headers:

| key   | 类型   | 描述      |
| ----- | ------ | --------- |
| token | string | 访问token |

Body:

```
{
    "user_id":"$user name$",
    "store_id":"$store name$",
    "keyword":"$search content$"
    "variable":"$error test judgment$"
}
```

| 变量名   | 类型   | 描述               | 是否可为空     |
| -------- | ------ | ------------------ | -------------- |
| user_id  | string | 用户名             | N              |
| store_id | string | 店铺名             | 全站搜索时为空 |
| keyword  | string | 搜索内容（已分词） | N              |
| variable | bool   | 判断是否为错误测试 | N              |

**Response**

Status Code:

| 码   | 描述                   |
| ---- | ---------------------- |
| 200  | 搜索成功，返回相应内容 |
| 511  | 不存在用户名           |
| 513  | 不存在店铺名           |
| 522  | 无相关搜索结果         |
| 528  | SQLAlchemyError        |
| 530  | BaseException          |

Body:

```
{   
    "message":"$error message$",
    "pagenum":"number of pages",
    "row":"search result",
    "show":"the content displayed on the page"
}
```

| 变量名  | 类型   | 描述                                      | 是否可为空           |
| ------- | ------ | ----------------------------------------- | -------------------- |
| message | string | 返回错误消息，成功时为"ok"                | N                    |
| pagenum | int    | 搜索内容共可分成多少页（5条一页）         | 不成功时不返回该字段 |
| row     | list   | 所有的搜索结果                            | 不成功时不返回该字段 |
| show    | list   | 第一页应该显示的内容（长度一定小于等于5） | 不成功时不返回该字段 |

#### 分页显示（附加功能）

> 传入三个参数：用户名、选中的页数和搜索得到的全部结果。类似地，先调用 user_id_exist 函数判断用户名是否存在，否则返回相应 code and message。该函数实现很简单，计算得到在选中页面需要显示的结果（show）即可，最后返回显示内容和所有搜索结果（以便可以连续选择页面）。

**请求地址** `POST` `/searcher/show_pages`

**Request**

Headers:

| key   | 类型   | 描述      |
| ----- | ------ | --------- |
| token | string | 访问token |

Body:

```
{
    "user_id":"$user name$",
    "page":"$the selected page$",
    "content":"$search content$"
    "variable":"$error test judgment$"
}
```

| 变量名   | 类型   | 描述               | 是否可为空 |
| -------- | ------ | ------------------ | ---------- |
| user_id  | string | 用户名             | N          |
| page     | string | 选中的要显示的页面 | N          |
| content  | string | 全部搜索结果       | N          |
| variable | bool   | 判断是否为错误测试 | N          |

**Response**

Status Code:

| 码   | 描述                   |
| ---- | ---------------------- |
| 200  | 搜索成功，返回相应内容 |
| 511  | 不存在用户名           |
| 528  | SQLAlchemyError        |
| 530  | BaseException          |

Body:

```
{   
    "message":"$error message$",
    "pagenum":"number of pages",
    "row":"search result",
    "show":"the content displayed on the page"
}
```

| 变量名  | 类型   | 描述                                           | 是否可为空 |
| ------- | ------ | ---------------------------------------------- | ---------- |
| message | string | 返回错误消息，成功时为"ok"                     | N          |
| row     | list   | 所有的搜索结果                                 | N          |
| show    | list   | 选中的页面应该显示的内容（长度一定小于总页数） | N          |

### 其他

#### 未支付订单超时自动取消

> 每次查询订单时（买家查询自己的历史订单/卖家查询自己商店的订单），如果查询得到的未支付订单超时，则自动取消该订单，从数据库中删去。 

Status Code:  

| 码      | 描述                                             |
| ------- | ------------------------------------------------ |
| 200     | 查询成功                                         |
| 523/521 | 删去已超时的未支付订单后，该商店或该用户没有订单 |

**test**  

两个订单，一个超时，查询到一个/一个订单超时，该买家无订单/一个订单超时，该商店无订单  

## 测试方法

```bash
 bash script/test.sh
```

## 测试结果

```bash
============================= test session starts =============================
platform win32 -- Python 3.10.8, pytest-7.1.2, pluggy-1.0.0 -- D:\ProgramData\Anaconda3\envs\db_bookstore\python.exe
cachedir: .pytest_cache
rootdir: D:\Coding_Documents\class_practice\db\pj2\bookstore_CDMS2022
collecting ... frontend begin test
2022-12-09 15:20:58,376 INFO sqlalchemy.engine.Engine select pg_catalog.version()
2022-12-09 15:20:58,376 INFO sqlalchemy.engine.Engine [raw sql] {}
2022-12-09 15:20:58,389 INFO sqlalchemy.engine.Engine select current_schema()
2022-12-09 15:20:58,390 INFO sqlalchemy.engine.Engine [raw sql] {}
2022-12-09 15:20:58,394 INFO sqlalchemy.engine.Engine show standard_conforming_strings
2022-12-09 15:20:58,395 INFO sqlalchemy.engine.Engine [raw sql] {}
2022-12-09 15:20:58,401 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2022-12-09 15:20:58,405 INFO sqlalchemy.engine.Engine select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where pg_catalog.pg_table_is_visible(c.oid) and relname=%(name)s
2022-12-09 15:20:58,406 INFO sqlalchemy.engine.Engine [generated in 0.00154s] {'name': 'bookstore_book'}
2022-12-09 15:20:58,412 INFO sqlalchemy.engine.Engine select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where pg_catalog.pg_table_is_visible(c.oid) and relname=%(name)s
2022-12-09 15:20:58,413 INFO sqlalchemy.engine.Engine [cached since 0.009347s ago] {'name': 'bookstore_new_order'}
2022-12-09 15:20:58,417 INFO sqlalchemy.engine.Engine select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where pg_catalog.pg_table_is_visible(c.oid) and relname=%(name)s
2022-12-09 15:20:58,417 INFO sqlalchemy.engine.Engine [cached since 0.0134s ago] {'name': 'bookstore_new_order_detail'}
2022-12-09 15:20:58,420 INFO sqlalchemy.engine.Engine select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where pg_catalog.pg_table_is_visible(c.oid) and relname=%(name)s
2022-12-09 15:20:58,421 INFO sqlalchemy.engine.Engine [cached since 0.01722s ago] {'name': 'bookstore_store'}
2022-12-09 15:20:58,425 INFO sqlalchemy.engine.Engine select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where pg_catalog.pg_table_is_visible(c.oid) and relname=%(name)s
2022-12-09 15:20:58,425 INFO sqlalchemy.engine.Engine [cached since 0.02165s ago] {'name': 'bookstore_user'}
2022-12-09 15:20:58,429 INFO sqlalchemy.engine.Engine select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where pg_catalog.pg_table_is_visible(c.oid) and relname=%(name)s
2022-12-09 15:20:58,430 INFO sqlalchemy.engine.Engine [cached since 0.02605s ago] {'name': 'bookstore_user_store'}
2022-12-09 15:20:58,433 INFO sqlalchemy.engine.Engine COMMIT
 * Serving Flask app 'be.serve' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
collected 65 items

fe/test/test_add_book.py::TestAddBook::test_ok PASSED                    [  1%]
fe/test/test_add_book.py::TestAddBook::test_error_non_exist_store_id PASSED [  3%]
fe/test/test_add_book.py::TestAddBook::test_error_exist_book_id PASSED   [  4%]
fe/test/test_add_book.py::TestAddBook::test_error_non_exist_user_id PASSED [  6%]
fe/test/test_add_funds.py::TestAddFunds::test_ok PASSED                  [  7%]
fe/test/test_add_funds.py::TestAddFunds::test_error_user_id PASSED       [  9%]
fe/test/test_add_funds.py::TestAddFunds::test_error_password PASSED      [ 10%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_error_user_id PASSED [ 12%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_error_store_id PASSED [ 13%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_error_book_id PASSED [ 15%]
fe/test/test_add_stock_level.py::TestAddStockLevel::test_ok PASSED       [ 16%]
fe/test/test_bench.py::test_bench PASSED                                 [ 18%]
fe/test/test_cancel_order.py::TestCancelOrder::test_unpaid_ok PASSED     [ 20%]
fe/test/test_cancel_order.py::TestCancelOrder::test_paid_ok PASSED       [ 21%]
fe/test/test_cancel_order.py::TestCancelOrder::test_error_delivered_received PASSED [ 23%]
fe/test/test_cancel_order.py::TestCancelOrder::test_error_order PASSED   [ 24%]
fe/test/test_cancel_order.py::TestCancelOrder::test_error_repeat PASSED  [ 26%]
fe/test/test_cancel_order.py::TestCancelOrder::test_error_user_id PASSED [ 27%]
fe/test/test_cancel_order.py::TestCancelOrder::test_error_seller_no_funds PASSED [ 29%]
fe/test/test_create_store.py::TestCreateStore::test_ok PASSED            [ 30%]
fe/test/test_create_store.py::TestCreateStore::test_error_exist_store_id PASSED [ 32%]
fe/test/test_deliver.py::TestDeliver::test_error_order_id PASSED         [ 33%]
fe/test/test_deliver.py::TestDeliver::test_error_deliver_error PASSED    [ 35%]
fe/test/test_deliver.py::TestDeliver::test_ok PASSED                     [ 36%]
fe/test/test_deliver.py::TestDeliver::test_error_repeat_deliver PASSED   [ 38%]
fe/test/test_deliver.py::TestDeliver::test_error_seller_id PASSED        [ 40%]
fe/test/test_login.py::TestLogin::test_ok PASSED                         [ 41%]
fe/test/test_login.py::TestLogin::test_error_user_id PASSED              [ 43%]
fe/test/test_login.py::TestLogin::test_error_password PASSED             [ 44%]
fe/test/test_new_order.py::TestNewOrder::test_non_exist_book_id PASSED   [ 46%]
fe/test/test_new_order.py::TestNewOrder::test_low_stock_level PASSED     [ 47%]
fe/test/test_new_order.py::TestNewOrder::test_ok PASSED                  [ 49%]
fe/test/test_new_order.py::TestNewOrder::test_non_exist_user_id PASSED   [ 50%]
fe/test/test_new_order.py::TestNewOrder::test_non_exist_store_id PASSED  [ 52%]
fe/test/test_password.py::TestPassword::test_ok PASSED                   [ 53%]
fe/test/test_password.py::TestPassword::test_error_password PASSED       [ 55%]
fe/test/test_password.py::TestPassword::test_error_user_id PASSED        [ 56%]
fe/test/test_payment.py::TestPayment::test_ok PASSED                     [ 58%]
fe/test/test_payment.py::TestPayment::test_authorization_error PASSED    [ 60%]
fe/test/test_payment.py::TestPayment::test_not_suff_funds PASSED         [ 61%]
fe/test/test_payment.py::TestPayment::test_repeat_pay PASSED             [ 63%]
fe/test/test_receive.py::TestReceive::test_error_status_unpaid PASSED    [ 64%]
fe/test/test_receive.py::TestReceive::test_error_status_undelivered PASSED [ 66%]
fe/test/test_receive.py::TestReceive::test_ok PASSED                     [ 67%]
fe/test/test_receive.py::TestReceive::test_error_no_order PASSED         [ 69%]
fe/test/test_receive.py::TestReceive::test_error_repeat_receive PASSED   [ 70%]
fe/test/test_receive.py::TestReceive::test_error_user_id PASSED          [ 72%]
fe/test/test_register.py::TestRegister::test_register_ok PASSED          [ 73%]
fe/test/test_register.py::TestRegister::test_unregister_ok PASSED        [ 75%]
fe/test/test_register.py::TestRegister::test_unregister_error_authorization PASSED [ 76%]
fe/test/test_register.py::TestRegister::test_register_error_exist_user_id PASSED [ 78%]
fe/test/test_search.py::TestSearch::test_store_ok PASSED                 [ 80%]
fe/test/test_search.py::TestSearch::test_all_ok PASSED                   [ 81%]
fe/test/test_search.py::TestSearch::test_error_non_exist_search PASSED   [ 83%]
fe/test/test_search.py::TestSearch::test_non_exist_user_id PASSED        [ 84%]
fe/test/test_search.py::TestSearch::test_non_exist_store_id PASSED       [ 86%]
fe/test/test_search_order.py::TestSearchOrder::test_buyer_search PASSED  [ 87%]
fe/test/test_search_order.py::TestSearchOrder::test_error_no_order PASSED [ 89%]
fe/test/test_search_order.py::TestSearchOrder::test_error_no_detail PASSED [ 90%]
fe/test/test_seller_search.py::TestSellerSearch::test_seller_search PASSED [ 92%]
fe/test/test_seller_search.py::TestSellerSearch::test_error_no_order PASSED [ 93%]
fe/test/test_seller_search.py::TestSellerSearch::test_error_no_detail PASSED [ 95%]
fe/test/test_timeout_cancel.py::TestTimeOut::test_timeout_cancel_buyer PASSED [ 96%]
fe/test/test_timeout_cancel.py::TestTimeOut::test_timeout_no_order_buyer PASSED [ 98%]
fe/test/test_timeout_cancel.py::TestTimeOut::test_timeout_cancel_seller PASSED [100%]

============================== warnings summary ===============================
..\..\..\..\..\ProgramData\Anaconda3\envs\db_bookstore\lib\site-packages\win32\lib\pywintypes.py:51
..\..\..\..\..\ProgramData\Anaconda3\envs\db_bookstore\lib\site-packages\win32\lib\pywintypes.py:51
  D:\ProgramData\Anaconda3\envs\db_bookstore\lib\site-packages\win32\lib\pywintypes.py:51: DeprecationWarning: getargs: The 'u' format is deprecated. Use 'U' instead.
    found = _win32sysloader.GetModuleFilename(filename)

..\..\..\..\..\ProgramData\Anaconda3\envs\db_bookstore\lib\site-packages\win32\lib\pywintypes.py:65
  D:\ProgramData\Anaconda3\envs\db_bookstore\lib\site-packages\win32\lib\pywintypes.py:65: DeprecationWarning: getargs: The 'u' format is deprecated. Use 'U' instead.
    found = _win32sysloader.LoadModule(filename)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 65 passed, 3 warnings in 1705.59s (0:28:25) =================
frontend end test
No data to combine
Name                              Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------------------
be\__init__.py                        0      0      0      0   100%
be\app.py                             3      3      2      0     0%
be\model\__init__.py                  0      0      0      0   100%
be\model\buyer.py                   271     52    148     25    78%
be\model\db_conn.py                  24      0     14      0   100%
be\model\error.py                    31      1      0      0    97%
be\model\orm_models.py               57      0     12      0   100%
be\model\searcher.py                 50     12     26      4    74%
be\model\seller.py                  130     31     76      7    75%
be\model\store.py                    28      1      4      1    94%
be\model\user.py                    132     23     58     10    78%
be\serve.py                          37      1      2      1    95%
be\view\__init__.py                   0      0      0      0   100%
be\view\auth.py                      42      0      0      0   100%
be\view\buyer.py                     68      0      8      0   100%
be\view\searcher.py                  42      2     12      1    94%
be\view\seller.py                    58      0      6      0   100%
fe\__init__.py                        0      0      0      0   100%
fe\access\__init__.py                 0      0      0      0   100%
fe\access\auth.py                    31      0      2      0   100%
fe\access\book.py                    63      0     18      1    99%
fe\access\buyer.py                   55      0      4      0   100%
fe\access\new_buyer.py                8      0      0      0   100%
fe\access\new_searcher.py             8      0      0      0   100%
fe\access\new_seller.py               8      0      0      0   100%
fe\access\searcher.py                33      1      6      1    95%
fe\access\seller.py                  45      0      2      0   100%
fe\bench\__init__.py                  0      0      0      0   100%
fe\bench\run.py                      13      0      6      0   100%
fe\bench\session.py                  47      0     14      1    98%
fe\bench\workload.py                125      1     28      2    98%
fe\conf.py                           11      0      0      0   100%
fe\conftest.py                       17      0      0      0   100%
fe\test\add_store_book.py            46      2     18      2    94%
fe\test\gen_book_data.py             48      0     18      0   100%
fe\test\test_add_book.py             36      0     12      0   100%
fe\test\test_add_funds.py            23      0      2      0   100%
fe\test\test_add_stock_level.py      39      0     12      0   100%
fe\test\test_bench.py                 6      2      0      0    67%
fe\test\test_cancel_order.py         76      1      6      1    98%
fe\test\test_create_store.py         20      0      2      0   100%
fe\test\test_deliver.py              59      1      6      1    97%
fe\test\test_login.py                28      0      2      0   100%
fe\test\test_new_order.py            40      0      2      0   100%
fe\test\test_password.py             33      0      2      0   100%
fe\test\test_payment.py              60      1      6      1    97%
fe\test\test_receive.py              66      1      6      1    97%
fe\test\test_register.py             31      0      2      0   100%
fe\test\test_search.py               53      0      6      2    97%
fe\test\test_search_order.py         35      0      2      0   100%
fe\test\test_seller_search.py        33      0      2      0   100%
fe\test\test_timeout_cancel.py       50      0      2      0   100%
-------------------------------------------------------------------
TOTAL                              2219    136    556     62    91%
```

* **65**个测试用例全部通过
* 测试覆盖率为**91%**

详情可以至`test_result/htmlcov/index.html`查看。

## 附录

**`10205501460吴陆盟`**

>**版本管理**
>
>我们使用`git`进行版本管理，并在`github`上建立仓库以托管代码。
>
><img src="D:\Coding_Documents\class_practice\db\pj2\bookstore_CDMS2022\markdown\main.assets\网页捕获_9-12-2022_162745_github.com.jpeg" alt="网页捕获_9-12-2022_162745_github.com" style="zoom:25%;" />
>
>**demo的错误指正**
>
>`be\model\buyer.py` 的`payment()` 中：
>
>```python
>cursor = conn.execute("UPDATE user set balance = balance - ?"
>                                  "WHERE user_id = ? AND balance >= ?",
>                                  (total_price, buyer_id, total_price))
>if cursor.rowcount == 0:
>	return error.error_not_sufficient_funds(order_id)
>
>cursor = conn.execute("UPDATE user set balance = balance + ?"
>                                  "WHERE user_id = ?",
>                                  (total_price, buyer_id))
>```
>
>第二次`UPDATE`时 本应将`balance`加到`seller`上，但加给了`buyer`。应将`buyer_id`改为`seller_id`。
>
>**心得体会**
>
>在进行团队开发时，应当做到以下几点
>
>* 统一开发环境
>* 善用版本管理工具
>* 解耦不同功能模块，便于分工
>
>通过本次大作业，我对关系型数据库的设计、事务处理的理解进一步加深了。

****

**`10205501407李思涵`**

> **创建索引 `jieba_book.py`**  
>
> 首先，在原来的 book 表中新建一个 token 字段，用于储存 GIN索引。读取数据库，对搜索的范围（标题、作者、关键词、图书信息）使用 jieba 进行分词，用空格隔开，以便后面使用 to_tsvector 函数的 simple 方法进行转换。再使用 setweight 对不同的内容赋予权重，我设置的是标题优先于关键词优先于图书信息优先于作者。最后将对应内容更新至token字段，成功创建索引。  
>
> 一开始我遇到很多问题，包括对 GIN索引的不熟悉，分词失败等，后来在助教的指导下找到了好的方法。我这里是直接用 sql 语句创建的索引，我尝试使用 ORM 但是一直出错，可能是语法有点问题。我后面还遇到了一个问题就是 后面查找时发现每本书计算出的分数都相同，后面才发现是我把所有 book 元组的 token 整合到一起最后每个元组都重复储存了同一个，之后我分别用列表储存标题和分词结果对应赋值 token 解决了问题。  
>
> **测试过程**
>
> 整个搜索功能的测试分为五个部分，分别测试：店铺内搜索、全站搜索、搜索结果不存在、用户名不存在、店铺名不存在。  
>
> 在测试之前使用函数 def pre_run_initialization() 定义相关参数：self.store_id1 为随机生 成的店铺名，self.store_id0 为空字符串表示全站搜索；self.add1 和 self.add0 新建 AddStoreBook 类。
> 该类实现代码我写在 fe\test\add_store_book.py 中，接收参数store_id，当店铺名为空时随机创建5到 20个店铺，向其中随机插入图书，否则就根据传入的店铺名指定创建并插入图书；self.keyword1 为查询关键字，self.keyword0为一个生僻字，为了后面查询不到结果的test。  
>
> 在具体的5个test中，先调用 AddStoreBook 类的 add 方法新建店铺并插入图书。在两个 test_ok 中，赋值布尔变量 True，接收 search 的正确的四个返回参数，如果总页数超过1，随机选中1个页面（小于总页数），调用 show_pages 实现分页显示，判断两个 code 都等于200。在三个 error测试中，赋值布尔变量 False，接收 search 的一个返回参数 code，判断其不等于200。
>
> **心得体会**
>
> 对整个搜索功能的实现，我主要遇到以下问题：前后端传参，如何结合正确测试和错误测试以及 GIN索引的创建和使用。  
>
> 对于前后端传参，一是数量的匹配，二是参数类型。因为正确测试和错误测试传递到前端的参数数量不同，所以不能以同一个格式来接收。而在参数类型方面，一开始我发现后端传回的搜索结果前端一直接收不到，后来经过一系列的类型转换才成功传递。对于如何结合正确测试和错误测试，主要就是在参数数量上体现的差别，所以我设置了一个布尔变量，通过判断这个变量选择不同的传参语句。对于 GIN索引的创建和使用，这是整个实现过程对于我挑战最大的地方，因为之前没有接触过，网上参考的资料也不是很多，所以一度陷入困境。感谢助教对我不厌其烦地答疑和发给我的知乎链接，非常有用！后面我又找到两个类似的，虽然是 JAVA 的，但是参考价值很大。我深入理解了 GIN索引的创建逻辑和查找时的使用方法，学会了相关函数的定义和使用，进一步提升了使用 jieba 分词的能力。  
>
> 当然，还有不得不提的各种配置环境和安包的问题。每次做大作业这个环节都是最费时和让人烦躁的。一开始我运行出来始终 response 500，困扰我很久，但同样的代码在组员的电脑上又可以成功运行。所以挣扎了很久，最后还是重新创建 conda 的虚拟环境并安装相关的各种包，幸好是成功解决了问题。后面安装 jieba 包也挺麻烦，具体的倒也不讲了。  
>
> 总之，我收获了很多实际应用的经验，编程能力也有所提高。

****

**`10205501420许琪`**

> **中间的问题和bug**  
>
> 1. 状态码一直报错为530  
>
>    解决方法：降低flask和Werkzeug版本为2.0.0后重启  
>
> 2. 后端传json文件一直报错UnicodeEncodeError: 'gbk' codec can't encode character '\ufffd' in position 494: illegal multibyte sequence，这个\ufffd的码本应该不存在于json中，寻找原因无果，print前后端传递的内容调试后，突然解决。  
>
> 3. 后端接口函数返回的参数个数不同
>    解决方法：参考new_order的函数写法，在无值的情况下，在error后加上 + ("",)，从而达到返回参数个数相同的目的  
>
> **心得体会**  
>
> 数据库的事务处理需要考虑多种错误情况，当同时对多个表进行修改时，放在一个session中能够解决事务中断或是冲突的情况，一整个事务回滚。  
>
> 测试代码的编写应当考虑到多种情况，仅是实现正确情况的测试是不够的，错误返回的测试也很重要。  
>
> 前后端的json文件传递可以通过print后端/前端获得的信息进行调试。  

