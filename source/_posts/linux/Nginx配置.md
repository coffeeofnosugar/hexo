---
title: 【Linux】Nginx配置
date: 2024-08-02 22:01:06
tags: 
  - Linux
  - Nginx
---

---

### 命令

```bash
nginx -t  # 检测配置文件
nginx -s reload # 重载配置文件
```







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

root会与URI的剩余部分（例子中为"/i/"）拼接，而alias不会

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





这里贴一个我自己的完整配置

```bash

#user  nobody;
worker_processes  1;

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';

    #access_log  logs/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;

    server {
        listen       80;
        server_name  www.coffeeofnosugar.top coffeeofnosugar.top;
	return 301 https://www.coffeeofnosugar.top;
    }



    # another virtual host using mix of IP-, name-, and port-based configuration
    #
    #server {
    #    listen       8000;
    #    listen       somename:8080;
    #    server_name  somename  alias  another.alias;

    #    location / {
    #        root   html;
    #        index  index.html index.htm;
    #    }
    #}


    # HTTPS server
    
    server {
        listen       443 ssl;
        server_name  www.coffeeofnosugar.top coffeeofnosugar.top;

        ssl_certificate      ../coffeeofnosugar.top.pem;
        ssl_certificate_key  ../coffeeofnosugar.top.key;

	#ssl_session_cache    shared:SSL:1m;
	ssl_session_timeout  5m;

	#ssl_ciphers  HIGH:!aNULL:!MD5;
	#ssl_prefer_server_ciphers  on;
	
	location /blog/ {
		root /usr/local/nginx/html;
	}

	location / {
		root /usr/local/nginx/html/blog;
		index index.html;
    	}
	
	location ~ ^/(unitygame|godot|addressable)/ {
		root /usr/local/nginx/html/;
	}
    }
}

```





---

### 参考连接

[Nginx Location 配置讲解](https://www.jianshu.com/p/f84e0c1a9bc6)
