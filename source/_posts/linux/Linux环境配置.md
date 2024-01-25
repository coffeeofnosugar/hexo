---
title: 【Linux】Linux环境配置
date: 2024-01-25 09:14:06
tags: Linux
---

### 前言

配置环境变量的位置在`/etc/profile`文件中(系统级别的配置文件)
`~/.bashrc`是用户级别的配置文件

在修改`/etc/profile`之后需要执行`source /etc/profile`命令使修改内容生效
`~/.bashrc`是该用户每次登入时会自动运行。以root用户进入时会执行`/root/.bashrc`配置文件，以steam用户进入会执行`/home/steam/.bashrc`配置文件

两个文件可以实现完美的搭配：

1. 修改`/etc/profile`配置文件实现自己的需求，如`export PS1='[\t \u@\h \w]\$ '`
2. 在`~/.bashrc`文件末尾添加`source /etc/profile`

这样在每次用户进入后都会执行一遍`source /etc/profile`命令，使`/etc/profile`配置文件生效



### 创建快捷方式

在`/usr/bin/`路径下创建一个`pbulic`快捷方式，使其指向`/home/hexo/public`

```shell
ln -sf /home/hexo/public /usr/bin/public
```

- `ln`：创建链接命令
- `-s`：表示创建软链接
- `-f`：表示在目标文件存在时强制删除并重新创建

`public`可以是文件夹，也可以是文本文件，也可以是执行文件（linux一个路径下不允许同时存在同名文件，同名的文件夹和文本文件也不行，所以不用担心索引错）
不管是什么，在访问`/usr/bin/public`时等同于访问`/home/hexo/public`

- 文件夹：`cd /usr/bin/public`等同于`cd /home/hexo/public`
- 文本文件：`vim /usr/bin/public`等同于`vim /home/hexo/public`
- 执行文件：`/usr/bin/public`等同于`/home/hexo/public`

执行文件最好放在`/usr/bin/`路径下，该路径下的执行文件是全局可用的
如，使用`ln -s /usr/local/nginx/sbin/nginx /usr/bin/nginx`创建了nginx的快捷方式，则在任意路径下执行`nginx`都等同于执行`/usr/local/nginx/sbin/nginx`

### 使用systemctl让服务器在后台运行

需要在`/etc/systemd/system/`路径下创建后缀为`.service`服务器配置文件，如`vim /etc/systemd/system/pal.service`

文件内容

```tex
[Unit]
# 服务器简介
Descripteion=pal server
# 前置service，都在/etc/systemd/system/下，network.target是连接上网络
After=network.target  XXX.service

[Service]
# 指定服务器运行的用户和组
User=yourusername
Group=yourgroupname
# 定义服务器在退出后是否自动重启
Restart=always
# 停止和重新加载服务时执行的命令
ExecStop=/path/to/stop/command
ExecReload=/path/to/reload/command
```

### 配置shell命令提示符

`PS1`代表提示符的变量，可以在shell中输入`echo $PS1`查看当前`PS1`的值

个人喜欢的一个配置`export PS1='[\t \u@\h \w]\$ '`

| 缩写 | 含义                                                   |
| ---- | ------------------------------------------------------ |
| \d   | 代表日期，格式为weekday month date                     |
| \H   | 完整的主机名称                                         |
| \h   | 仅主机的第一个名字                                     |
| \t   | 显示24小时格式的时间，HHMMSS                           |
| \T   | 显示12小时格式的时间                                   |
| \A   | 显示24小时格式的时间，HHMM                             |
| \u   | 当前账户的账号名称                                     |
| \v   | BASH的版本信息                                         |
| \w   | 完整的工作目录名称，家目录会以~显示                    |
| \W   | 利用basename去的工作目录名称，所以只会列出最后一个目录 |
| \#   | 下达的第几个命令                                       |
| \$   | 提示字符，如果是root，提示符为#，普通用户则为$         |

