---
title: 【Git】拉取部分文件
date: 2024-06-10 17:32:06
tags: Git
---

<link rel="stylesheet" href="/../css/center.css">
<link rel="stylesheet" href="/../css/images.css">

## 拉取部分文件

### 使用Sparse Checkout

1. 使用`git init`初始化仓库
2. 使用`git remote add origin [远程仓库地址]`将远程仓库添加到本地仓库
3. 使用`git config core.sparsecheckout true`将Git配置为使用sparse checkout模式
4. 编辑`.git/info/sparse-checkout`文件来指定需要拉取的目录
5. 使用`git pull origin [分支名]`拉取代码

### 使用Submodule

Submodule：将一个仓库设置为另一个仓库的子项目

1. 使用`git submodule add [子项目仓库地址] [子项目路径]`命令将子项目仓库添加到主项目
2. 通过`git submodule init`初始化子项目
3. 使用`git submodule update`更新子项目代码
