---
title: 【Linux】Linux基础命令
date: 2023-08-22 10:02:06
tags: Linux
---



---

### 用户

#### 创建用户

```shell
sudo useradd -m -s /bin/bash {username}
```

- `-m`：创建用户的同时，创建用户的`/home/{usrname}`目录
- `-s /bin/bash`：指定用户的默认登入shell为Bash

> 如果不用`-s /bin/bash`会出现无法使用上下左右方向键的问题
> 使用`cat /etc/passwd`可以看到`{username}`的登入shell是/bin/sh
> 使用`ls -l /bin/sh`，发现/bin/sh -> dash
> 修改连接目录`sudo ln -sf /bin/bash /bin/sh`，重新登入账户就可以了

```shell
sudo passwd {username}
```

为新用户设置密码，需要输入两次

#### 删除用户

```shell
sudo userdel -r {username}
```

删除用户及其相关的文件，包括`/home/{username}`文件

#### 给新用户root权限

通过将新用户添加到sudo组来给予root权限

```shell
sudo usermod -aG sudo {username}
```

验证：执行`sudo ls /root`，需要输入用户密码确认权限

#### 查看用户和组

| 命令              | 解释                                 |
| ----------------- | ------------------------------------ |
| `cat /etc/passwd` | 列出所有用户信息，每一行对应一个用户 |
| `who`或者`w`      | 查看当前登入的用户                   |
| `id {username}`   | 查看指定用户                         |

> `/etc/passwd`文件内容：
>
> ```
> root:x:0:0:root:/root:/bin/bash
> steam:x:1000:1000::/home/steam:/bin/sh
> ```
>
> 使用`:`分割
>
> - steam：用户名
> - x：加密的密码字段（为了安全不再存在该文件下，而是存在`/etc/shadow`下）
> - 1000：用户ID（UID）
> - 1000：组ID（GID）
> - **：用户描述信息，一般为空
> - `/home/steam`：用户的主目录
> - `/bin/sh`：用户登入的shell

| 命令                | 解释                         |
| ------------------- | ---------------------------- |
| `cat /etc/group`    | 查看所有组，每一行对应一个组 |
| `groups {username}` | 查看`{username}`所在组       |



---

### 防火墙 

#### 基础命令

| 基础命令                               | 效果                   |
| -------------------------------------- | ---------------------- |
| `systemctl start firewalld.service`    | 开启防火墙             |
| `systemctl status firewalld.service`   | 查看防火墙状态         |
| `systemctl stop firewalld.service`     | 关闭防火墙             |
| `systemctl enable firewalld.service`   | 开启时自启             |
| `systemctl disable firewall.service`   | 关闭开机自启           |
| `systemctl is-enable firewall.service` | 查看服务是否开机自启   |
| `systemctl --failed`                   | 查看启动失败的服务列表 |

#### 配置防火墙

| 命令                                                       | 效果                                                    |
| ---------------------------------------------------------- | ------------------------------------------------------- |
| `firewall-cmd --zone=public --list-ports`                  | 查看开放的端口                                          |
| `firewall-cmd --reload`                                    | 重新载入防火墙                                          |
| `firewall-cmd --zone=public --add-port=80/tcp --permanent` | 开放80端口，`--premanent`表示永久开放，重启后也依然开放 |

每次在配置完防火墙之后需使用`firewall-cmd --reload`更新配置
