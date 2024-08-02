---
title: 【Linux】Nginx配置
date: 2023-08-21 20:50:06
tags: 
  - Linux
  - Nginx
---



---

### 配置文件

配置文件为：`./nginx/conf/nginx.conf`

静态文件为：`./nginx/html/`

#### location

##### 用法

`location [ = | ~ | ~* | ^~ ] uri { ... }`，其中`|`表示你可能会用到的语法

- `=`：精确匹配
- `~`：区分大小写的正则匹配
- `~*`：不区分大小写的正则匹配
- `^~`：uri以某个字符串开头

```shell
local ^~ /unitygame/ {
    root /usr/local/nginx/html;
}

# /unitygame/3drpg		return /usr/local/nginx/html/unitygame/3drpg/index.html
```

- `/unitygame/3drpg`：通用匹配
- `/`：默认匹配

##### 顺序

优先级：`=` > `^~` > `~` > `~*` > 最长的通用匹配 > 默认匹配

- 经测试“默认匹配”最好放在“通用匹配后面”

#### root 与 alias 的区别

```shell
localtion /i/ {
    root /usr/local/nginx/html/blog;
}

# /i/top.gif		renturn /usr/local/nginx/html/blog/i/top.gif;

localtion /i/ {
    alias /usr/local/nginx/html/blog;
}

# /i/top.gif		return /usr/local/nginx/html/blog/top.gif;
```



---

### 参考连接

[Nginx Location 配置讲解](https://www.jianshu.com/p/f84e0c1a9bc6)
