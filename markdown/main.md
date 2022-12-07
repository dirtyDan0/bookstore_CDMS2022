# Bookstore

## 成员以及分工

| 学号        | 姓名   | 分工                                                     |
| ----------- | ------ | -------------------------------------------------------- |
| 10205501460 | 吴陆盟 | 实现并测试前60%功能；管理`Github`仓库；测试整个项目      |
| 10205501407 | 李思涵 | 实现并测试搜索接口的图书功能                             |
| 10205501420 | 许琪   | 实现并测试买家用户接口的收货功能和卖家用户接口的发货功能 |

## 关系数据库设计

### 概念设计



### ER图



### 关系模式



## 功能实现

### 数据库相关配置

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

#### Response

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

#### 付款

#### 充值

#### 收货（附加功能）

### 卖家用户接口

#### 创建店铺

#### 添加书籍信息

#### 添加书籍库存

#### 发货（附加功能）

### 搜索接口

#### 搜索图书（附加功能）

## 测试过程

## 测试结果

## 附录