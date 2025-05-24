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

配置一：

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

配置二：

> 注意：
>
> 1. 如果你当前的用户不是root时启动nginx，那么nginx的主进程(master process)是root用户，而工作进程会是nobody，而nobody不一定有html文件的读取权限，所以需要设置user为你当前登入的用户
>    <img src="/../images/linux/nginx配置/配置.png"></img>
> 2. root的路径必须是要是全路径
> 3. 如果还是连接不到网站，可以查看error.log日志，有详细的错误信息

```tex

user  ubuntu;		# 注意：需要设置用户名
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
        server_name  localhost;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;

        location / {
            root   /home/ubuntu/nginx/html;		# 需要全路径
            index  index.html;
        }

        #error_page  404              /404.html;

        # redirect server error pages to the static page /50x.html
        #
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }

        # proxy the PHP scripts to Apache listening on 127.0.0.1:80
        #
        #location ~ \.php$ {
        #    proxy_pass   http://127.0.0.1;
        #}

        # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
        #
        #location ~ \.php$ {
        #    root           html;
        #    fastcgi_pass   127.0.0.1:9000;
        #    fastcgi_index  index.php;
        #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
        #    include        fastcgi_params;
        #}

        # deny access to .htaccess files, if Apache's document root
        # concurs with nginx's one
        #
        #location ~ /\.ht {
        #    deny  all;
        #}
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
    #
    #server {
    #    listen       443 ssl;
    #    server_name  localhost;

    #    ssl_certificate      cert.pem;
    #    ssl_certificate_key  cert.key;

    #    ssl_session_cache    shared:SSL:1m;
    #    ssl_session_timeout  5m;

    #    ssl_ciphers  HIGH:!aNULL:!MD5;
    #    ssl_prefer_server_ciphers  on;

    #    location / {
    #        root   html;
    #        index  index.html index.htm;
    #    }
    #}

}

```





---

### 参考连接

[Nginx Location 配置讲解](https://www.jianshu.com/p/f84e0c1a9bc6)
