---
title: 【Linux】【Git】Linux系统安装Git
date: 2023-08-23 21:56:06
tags:
  - Linux
  - Git
---

### 下载

[下载包体](https://github.com/git/git/tags)

### 编译环境

```shell
sudo yum install libcurl-devel
sudo yum install expat-devel
sudo yum install asciidoc
sudo yum install xmlto
sudo yum install docbook2X
# 设置软连接
ln -s /usr/bin/db2x_docbook2texi /usr/bin/docbook2x-texi
ln -s /usr/bin/db2x_docbook2texi /usr/bin/docbook2texi
```

根据git官网的指示，安装相关依赖包：`yum install dh-autoreconf curl-devel expat-devel gettext-devel openssl-devel perl-devel zlib-devel libxslt asciidoc xmlto docbook2X autoconf install-info getopt`

### 安装

解压`tar -zxvf git-2.42.0.tar.gz`

编译`make prefix=/usr/local all doc info`

安装`make prefix=/usr/local install install-doc install-html install-info`

### 可能会出现的问题

提示找不到`docbook2x-texi`或者`docbook2texi`

在执行`yum install docbook2X`后设置软连接

```shell
ln -s /usr/bin/db2x_docbook2texi /usr/bin/docbook2x-texi
ln -s /usr/bin/db2x_docbook2texi /usr/bin/docbook2texi
```

### 参考

[使用源码方法在阿里云服务器CentOS 7安装Git](https://blog.csdn.net/qq_42108074/article/details/123027943)
