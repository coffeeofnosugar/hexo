---
title: 【Linux】MySQL
date: 2023-08-21 20:50:06
tags: Linux
---

### 安装

#### 下载包体

官网网址：[MySQL :: MySQL Community Downloads](https://dev.mysql.com/downloads/)

<img src="/../images/Linux/mysql/安装网址1.png"></img>

<img src="/../images/Linux/mysql/安装网址2.png"></img>

<img src="/../images/Linux/mysql/安装网址3.png"></img>

将文件解压到一个新建的文件夹中`tar -xvf mysql-8.0.33-1.el7.x86_64.rpm-bundle.tar -C mysql-8.0.33`

安装`openssl-devel`插件，mysql里有些rpm的安装依赖于该插件

#### 安装rpm包

依次执行以下命令

```bash
# 共享的 MySQL 通用文件，可能包括一些共享的配置文件等。这是 MySQL 安装的一部分，通常需要安装
rpm -ivh mysql-community-common-8.0.33-1.el7.x86_64.rpm
# MySQL 客户端插件，提供额外的功能和扩展。具体需要哪些插件取决于你的使用情况。你可以根据你的需要来决定是否安装这些插件。
rpm -ivh mysql-community-client-plugins-8.0.33-1.el7.x86_64.rpm
# MySQL 库文件，用于在应用程序中连接到 MySQL 数据库。这是 MySQL 连接所必需的，通常需要安装
rpm -ivh mysql-community-libs-8.0.33-1.el7.x86_64.rpm
# 共享的 MySQL 通用文件，可能包括一些共享的配置文件等。这是 MySQL 安装的一部分，通常需要安装
rpm -ivh mysql-community-libs-compat-8.0.33-1.el7.x86_64.rpm
# MySQL 开发包，包含开发所需的头文件和库文件。如果你打算在该系统上开发与 MySQL 相关的应用程序，你需要安装此包
rpm -ivh mysql-community-devel-8.0.33-1.el7.x86_64.rpm
# MySQL 客户端工具，用于连接和管理 MySQL 服务器。通常情况下，如果你计划从该系统上远程连接到其他 MySQL 服务器，你需要安装此包。如果你的系统不需要连接其他 MySQL 服务器，则可能不需要安装
rpm -ivh mysql-community-client-8.0.33-1.el7.x86_64.rpm
# ICU 数据文件，用于支持国际化和字符集处理。如果你的应用程序不需要特定的国际化功能，则可能不需要安装
rpm -ivh mysql-community-icu-data-files-8.0.33-1.el7.x86_64.rpm
# MySQL 服务器，用于托管数据库实例。如果你计划在该系统上安装 MySQL 数据库服务器，你需要安装此包
rpm -ivh mysql-community-server-8.0.33-1.el7.x86_64.rpm
```

---

### 常用命令

#### 启动

使用`systemctl start mysqld`命令启动服务器

rpm安装MySQL会自动生成一个随机密码，可以在`/var/log/mysqld.log`中查看

<img src="/../images/Linux/mysql/随机密码.png">

使用`mysql -u root -p`进入客户端

<img src="/../images/Linux/mysql/输入密码.png">

#### 设置密码

连接MySQL之后，使用`ALTER USER 'root'@'localhost' IDENTIFIED BY '123456789';`修改密码

<img src="/../images/Linux/mysql/设置密码.png">

出现`Your password does not satisfy the current policy requirements`提示，意思是您的密码不符合当前规定的要求，你要么就把你的密码设置得复杂点，要么就去降低密码的校验规则。

在 Linux 上安装 MySQL 时会自动安装一个校验密码的插件，默认密码检查策略要求密码必须包含：大小写字母、数字和特殊符号，并且长度不能少于8位。修改密码时新密码是否符合当前的策略，不满足则会提示ERROR

可以将这个限制密码位数设小一点，复杂度类型调底一点

```bash
# 将密码复杂度校验调整简单类型
set global validate_password.policy = 0;
# 设置密码最少位数限制为 4 位
set global validate_password.length = 4;
```

<img src="/../images/Linux/mysql/设置密码复杂度.png">
