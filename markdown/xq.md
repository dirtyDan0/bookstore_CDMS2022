## 功能1：订单收货和发货

### 发货

卖家权限接口： delivered

实现逻辑和数据库操作：  
传入卖家id和订单id  
检查订单是否存在：用order_id查询NewOrder表
是否属于该卖家：用user_id查询UserStore表  
检查订单状态：用order_id查询NewOrder表获取status  
如果订单状态为已支付，则将NewOrder表中该记录的status修改为已发货  
其他状态不允许修改订单状态为已发货。  

**请求地址：**
POST http://[address]/seller/delivered

**Request**

Body:

```json
{
    "user_id":"$user_id$",
    "order_id":"$order_id$"
}
```

| 变量名      | 类型   | 描述      | 是否可为空 |
|----------| ------ |---------|-------|
| user_id  | string | 卖家用户的id | N     |
| order_id | string | 卖家要发货的订单id | N     |

**Response**

Status Code:

| 码   | 描述                   |
|-----|----------------------|
| 200 | 发货成功                 |
| 401 | 权限错误，该订单的卖家不是该用户     |
| 518 | 无效订单                 |
| 520 | 不是已支付的订单：未支付/已发货/已收货 |

**test**  

order_id错误/未支付订单/重复发货/卖家id错误  

### 收货

买家权限接口： received

实现逻辑和数据库操作：  
传入买家id和订单id  
检查订单是否存在：用order_id查询NewOrder表  
是否属于该买家：用user_id查询UserStore表  
检查订单状态：用order_id查询NewOrder表获取status  
如果订单状态为已发货，则将NewOrder表中该记录的status修改为已收货  
其他状态不允许修改订单状态为已收货。  

**请求地址：**
POST http://[address]/buyer/received

**Request**

Body:
```json
{"user_id": "$user_id$", "order_id": "$order_id$"}
```

| 变量名      | 类型   | 描述         | 是否可为空 |
|----------| ------ |------------|-------|
| user_id  | string | 买家用户的id    | N     |
| order_id | string | 买家要收货的订单id | N     |

**Response**

Status Code:

| 码   | 描述                   |
|-----|----------------------|
| 200 | 收货成功                 |
| 401 | 权限错误，该订单的买家不是该用户     |
| 518 | 无效订单                 |
| 520 | 不是已发货的订单：未支付/已支付/已收货 |

**test**  

未支付订单/未发货订单/订单id错误/重复收货/买家id错误  

## 功能2：订单状态，订单查询和取消定单

### 订单状态
在NewOrder表增加status，该属性存储订单的状态，分为：  

未支付 -> 已支付 -> 已发货 -> 已收货  

### 订单查询

**买家查询自己所有的历史订单信息**  
买家权限接口：search_order  

实现逻辑和数据库操作：  
传入买家id  
检查该用户是否有订单：用user_id查询NewOrder表获取订单列表信息    
用查询到的order_id查询NewOrderDetail表获取订单具体信息
检查查询的detail是否为空，空则返回订单错误  
将订单和订单具体信息返回。    

**请求地址：**
POST http://[address]/buyer/search_order

**Request**

Body:
```json
{"user_id": "$user_id$"}
```

| 变量名      | 类型   | 描述         | 是否可为空 |
|----------| ------ |------------|-------|
| user_id  | string | 买家用户的id    | N     |

**Response**

Status Code:  

| 码   | 描述                   |
|-----|----------------------|
| 200 | 查询成功                 |
| 518 | 无效订单     |
| 521 | 用户没有订单               |

##### Body:
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

##### 属性说明：

| 变量名            | 类型 | 描述 | 是否可为空|
|----------------|---|---|---|
| order_id       | string | 订单号，只有返回200时才有效 | N |
| store_id       | string | 商店号，只有返回200时才有效 | N|
| time           | string | 订单创建时间 | N|
| status         | string | 订单状态 | N|
| detail         | list | 存储订单具体信息 | N|
| detail.book_id | string | 购买的书号 | N|
| detail.count   | int | 购买的数量 | N|
|  detail.price  | int | 书的价格 | N|

**test**  

买家id错误/订单没有内容

**卖家查询自己商店的所有订单**

实现逻辑和数据库操作：  
传入卖家id和商店id  
检查该商店是否有订单，用store_id查询NewOrder表获取订单列表信息    
用查询到的order_id查询NewOrderDetail表获取订单具体信息  
检查查询的detail是否为空，空则返回订单错误  
将订单和订单具体信息返回。  

卖家权限接口：seller_search

**请求地址：**
POST http://[address]/seller/seller_search

**Request**

Body:
```json
{"user_id": "$seller_id$","store_id": "$store_id$"}
```

| 变量名      | 类型   | 描述      | 是否可为空 |
|----------| ------ |---------|-------|
| user_id  | string | 卖家用户的id | N     |
| store_id | string | 要查询的商店id | N |

**Response**

Status Code:  

| 码   | 描述     |
|-----|--------|
| 200 | 查询成功   |
| 518 | 无效订单   |
| 523 | 商店没有订单 |

##### Body:
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

##### 属性说明：

| 变量名            | 类型 | 描述              | 是否可为空|
|----------------|---|-----------------|---|
| order_id       | string | 订单号，只有返回200时才有效 | N |
| user_id        | string | 买家号，只有返回200时才有效 | N|
| time           | string | 订单创建时间          | N|
| status         | string | 订单状态            | N|
| detail         | list | 存储订单具体信息        | N|
| detail.book_id | string | 购买的书号           | N|
| detail.count   | int | 购买的数量           | N|
| detail.price   | int | 书的价格            | N|

**test**  

卖家id错误/订单没有内容  

### 取消订单功能

取消订单的步骤：

1. 主动取消
取消订单接口：获取买家id和订单id  
用order_id查询NewOrder表获取订单信息  
检查商店id是否存在，status 不是已收货/已发货，用户id是买家id  
If 订单状态是未支付  
只需要修改仓库信息，order_id查询NewOrderDetail表获取订单购买的具体信息，更新相应store里的库存信息。
If 已支付  
需要修改仓库信息/余额变动，计算总金额，查询User表里商家id的记录判断商家的钱够不够扣除，够则扣除订单金额，在买家金额里加上相同金额。    
最后都要删除new_order/new_order_detail里的该订单记录    
2. 超时取消
超过一定时间未支付，自动取消  
每次查询，如果计算时间（当前时间 - 订单创建时间）>= 1s 删除订单  

**买家主动取消**  

买家权限接口：cancel_order  

**请求地址：**
POST http://[address]/buyer/cancel_order

**Request**

Body:
```json
{"user_id": "$user_id$", "order_id": "$order_id$"}
```

| 变量名      | 类型   | 描述         | 是否可为空 |
|----------| ------ |------------|-------|
| user_id  | string | 买家用户的id    | N     |
| order_id | string | 要取消的订单id | N |

**Response**

Status Code:  

| 码   | 描述                    |
|-----|-----------------------|
| 200 | 取消成功                  |
| 518 | 无效订单                  |
| 513 | 该商店id不存在              |
| 520 | 该状态不允许取消订单操作，已发货/已收货  |
| 401 | 权限错误                  |
| 515 | 不存在该book_id           |
| 514 | 该商店id对应的卖家不存在         |
| 511 | 该买家id不存在              |
| 519 | 买家已支付订单，取消订单时卖家的钱不够退回 |

**test**  

未支付/已支付订单取消成功  
已发货/已收货订单取消失败、订单id错误、重复取消、错误买家id、卖家的钱不够扣除  

**未支付订单超时自动取消**  

实现思路：  
每次查询订单时（买家查询自己的历史订单，卖家查询自己商店的订单），如果查询得到的未支付订单超时，则自动取消该订单，从数据库中删去。  

Status Code:  

| 码       | 描述                       |
|---------|--------------------------|
| 200     | 查询成功                     |
| 523/521 | 删去已超时的未支付订单后，该商店或该用户没有订单 |

**test**  

两个订单，一个超时，查询到一个/一个订单超时，该买家无订单/一个订单超时，该商店无订单  

**中间的问题和bug**  
1. 状态码一直报错为530  
    解决方法：降低flask和Werkzeug版本为2.0.0后重启  
2. 后端传json文件一直报错UnicodeEncodeError: 'gbk' codec can't encode character '\ufffd' in position 494: illegal multibyte sequence，这个\ufffd的码本应该不存在于json中，寻找原因无果，print前后端传递的内容调试后，突然解决。  
3. 后端接口函数返回的参数个数不同
    解决方法：参考new_order的函数写法，在无值的情况下，在error后加上 + ("",)，从而达到返回参数个数相同的目的  
