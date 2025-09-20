---
title: 【Linux】Linux基础命令
date: 2023-08-22 10:02:06
tags: Linux
---



---

### 用户

#### 切换用户

```shell
sudo -u {username} -s
```

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



---

### 文件操作

| cat  <fileName>             | 查看文件                           |
| --------------------------- | ---------------------------------- |
| touch  <fileName>           | 创建文件                           |
| mkdir -p  <dirName>         | 创建文件夹（-p 创建缺失的父目录）  |
| cp  fileName <pah>          | 复制文件(后面的地址，不用加文件名) |
| mv  <filename> <path>       | 移动文件                           |
| mv  <fileName1> <fileName2> | 修改文件名称                       |
| rm  <filename>              | 删除文件                           |
| rm -r  <dirName>            | 删除空文件夹 -f 强制删除，不用确认 |

| cd   |                    |
| ---- | ------------------ |
| pwd  | 显示当前所在路径   |
| cd - | 返回上一次所在路径 |



```bash
-rwxrw-r--   1 ubuntu root 1249 May 22 01:09 init.vim
```



1. 第一个字符：表示类型
   - -：普通文件
   - d：目录
   - l：软链接

2. 后续9个字符：表示权限

   - rwx：所有者可读可写可执行
   - rw-：所属组可读可写
   - r--：其他用户仅可读

   > 文件权限
   >
   > r:4  w:2  x:1
   >
   > owner = rwx = 4+2+1 =7
   >
   > chmod [-R] xyz <fileName>
   >
   > 将owner/group/others及其子文件都设置为可读可写可执行
   >
   > chmod -R 777 fileName

3. 硬链接数

   - 表示该文件的硬链接数量为1（即无其他硬链接指向此文件）
   - 如果是目录，此数字表示子目录数（至少为2，含 `.` 和 `..`）

   > 硬链接是同一个文件的**多个名称**（类似于一个人的多个别名）。
   >
   > 删除原始文件或任一硬链接，只要还存在至少一个硬链接，文件数据就不会被真正删除。
   >
   > 用途：
   >
   > 1. **备份与冗余**：通过硬链接保护重要文件（删除一个不影响其他）。
   > 2. **节省空间**：多个硬链接共享同一份数据，不占用额外磁盘空间。
   > 3. **版本控制**：某些工具（如 Git）内部使用硬链接优化存储。
   >
   > ```bash
   > # 创建硬链接
   > echo "Hello" > original.txt
   > ln original.txt hardlink.txt  # 创建硬链接
   > 
   > # 查看 inode（确认是否相同）
   > ls -i original.txt hardlink.txt
   > # 输出示例：12345 original.txt  12345 hardlink.txt
   > 
   > # 删除原始文件后，硬链接仍可访问
   > rm original.txt
   > cat hardlink.txt  # 正常输出 "Hello"
   > ```

4. 所属者和所属组

   - 所有者为ubuntu（**所有者（Owner）**：当前拥有文件控制权的用户（不一定是创建者）。）
   - 所属组为root

5. 文件大小

   - 1240字节（默认单位是字节，使用ls -lh可显示易读单位）

6. 最后修改时间

快捷方式

`ln -s /usr/local/nginx/sbin/nginx /usr/bin/nginx`

7. 实时查看log文件

```shell
tail -f /path/to/your/logfile.log
```

```shell
less +F /path/to/your/logfile.log
```







---

### 端口

| netstat  -lntp | 查看网络连接状态和端口情况                                   |
| -------------- | ------------------------------------------------------------ |
| lsof -i  :5000 | 查看5000端口的进程PID，然后可以使用sudo kill <PID>关闭这个进程 |



---

### 进程

| top                  | 查看系统实时状态，可以使用top  -b -d 10 -n 10 > top_log.txt 来将内容保存下来(每十秒保存一次，共保存10次) |
| -------------------- | ------------------------------------------------------------ |
| ps -ef               | 查看所有进程可以通过 ps  -ef \| grep <contetn>来筛选         |
| ps aux \| grep nginx | 查看nginx的进程                                              |

---

### 解压/压缩

| .tar    | tar xvf  FileName.tar             | 解压                                       |
| ------- | --------------------------------- | ------------------------------------------ |
|         | tar cvf  FileName.tar DirName     | 压缩 tar cvf  {newname.tar} {path/to/name} |
| .tar.xz | tar xvf  FileName.tar.xz          |                                            |
|         | tar cvf  FileName.tar DirName     |                                            |
| .tar.gz | tar  zxvf FileName.tar.gz         |                                            |
|         | tar  zcvf FileName.tar.gz DirName |                                            |
| zip     | unzip  FileName.zip               |                                            |
|         | zip  FileName.zip DirName         |                                            |
