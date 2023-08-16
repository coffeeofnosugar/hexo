---
title: 【Git】基础命令
date: 2023-08-12 11:17:06
tags: Git
---

<link rel="stylesheet" href="/../css/center.css">
<link rel="stylesheet" href="/../css/images.css">

## 合并分支

使用`git merge <branchName>`命令将`<branchName>`分支上的内容合并到当前所在的分支上

出现如下内容，说明自动合并发生了冲突，需要手动解决冲突

<img class="base" src="/../images/git/合并分支_冲突.png"></img>

使用`git status`查看冲突文件
<img class="base" src="/../images/git/合并分支_冲突文件.png"></img>

使用`git diff`查看冲突内容
<img class="base" src="/../images/git/合并分支_冲突内容.png"></img>

使用`vim <fielName>`编辑该文件，留下我们需要的内容
随便怎么改都行，你就把它想成是重新编辑文件，只不过给了你两个版本的提示

修改前：

<img class="base" src="/../images/git/合并分支_编辑文件.png"></img>

修改后：

<img class="base" src="/../images/git/合并分支_修复冲突.png"></img>

最后再重新提交一遍就成功的解决了冲突

<img class="base" src="/../images/git/合并分支_提交冲突文件.png"></img>

---



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