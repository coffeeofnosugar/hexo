---
title: 【Linux】Nginx安装
date: 2023-08-21 20:50:06
tags:
  - Linux
  - Nginx
---

### 安装

#### 下载包体

网站：[nginx: download](https://nginx.org/en/download.html)

<img src="/../images/linux/nginx安装/安装网站.png"></img>

#### 上传解压

`tar -zxvf nginx-1.24.0.tar.gz`

#### 编译

`./configure --prefix=/usr/local/nginx --with-http_stub_status_module --with-http_ssl_module`

`make`

`make install`

> 在执行`./configure`时如果出现报错缺少对应的模块，则安装对应的模块
>
> 1. 缺少PCRE，安装命令：`sudo apt install libpcre3 libpcre3-dev`
>
>    <img src="/../images/linux/nginx安装/缺少PCRE.png"></img>
>
> 2. 缺少SpenSSL，安装命令：`sudo apt install libssl-dev`
>
>    <img src="/../images/linux/nginx安装/缺少OpenSSL.png"></img>
>
>    

#### 环境配置

设置快捷键

`ln -s /usr/local/nginx/sbin/nginx /usr/bin/nginx`

这样执行/usr/bin/nginx就相当于执行了/usr/local/nginx/sbin/nginx

而/usr/bin/是全局可用的，所以在任何地方输入nginx都可以执行/usr/lcoal/nginx/sbin/nginx





使用下面命令实时查看log更新

```bash
less +F access.log
```

