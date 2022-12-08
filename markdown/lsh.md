#### 搜索图书（附加功能）
#### 搜索
**请求地址：**`POST` `/searcher/search`

**Request**

Headers:

| key   | 类型   | 描述      |
| ----- | ------ | --------- |
| token | string | 访问token |

Body:

```
{
    "user_id":"$user name$",
    "store_id":"$user password$",
    "keyword":"$terminal code$"
    "variable":
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

#### 分页显示
**请求地址：**`POST` `/searcher/show_pages`