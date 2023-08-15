---
title: 【Git】基础命令
date: 2023-08-12 11:17:06
tags: Git
---

<link rel="stylesheet" href="/../css/center.css">



## Git远程命令



```shell
// 查看绑定了哪些远程仓库
git remote -v
// 删除远程的绑定
git remote remove <name>
// 将本地仓库的内容推送到远程仓库的branch_name分支上
git push -u <origin_name> <branch_name>
// 将远程仓库的branch_name拉取到本地工作区
git pull <origin_name> <branch_name>
```

<center class="moderate">持续更新</center>