---
title: 【Git】合并分支及如何解决冲突
date: 2023-09-15 09:44:06
tags: Git
---

<link rel="stylesheet" href="/../css/center.css">
<link rel="stylesheet" href="/../css/images.css">


### 合并分支

#### 合并

使用`git merge <branchName>`命令将`<branchName>`分支上的内容合并到当前所在的分支上

`<branchName>` 可以是分支的名字，也可以是`commitID`

#### 出现冲突

出现如下内容，说明自动合并发生了冲突，需要手动解决冲突

<img class="base" src="/../images/git/合并分支_冲突.png"></img>

使用`git status`查看冲突文件
<img class="base" src="/../images/git/合并分支_冲突文件.png"></img>

使用`git diff`查看冲突内容
<img class="base" src="/../images/git/合并分支_冲突内容.png"></img>

### 解决冲突

#### 解决冲突的三种方法

##### 方法一:直接编辑

使用`vim <fielName>`编辑该文件，留下我们需要的内容
随便怎么改都行，你就把它想成是重新编辑文件，只不过给了你两个版本的提示

修改前：

<img class="base" src="/../images/git/合并分支_编辑文件.png"></img>

修改后：

<img class="base" src="/../images/git/合并分支_修复冲突.png"></img>

##### 方法二:保留选择的版本

选择当前分支的版本作为解决方案

```bash
git checkout --ours <fileName>
```

选择合并分支的版本

```bash
git checkout --theirs <fileName>
```

##### 方法三：强行退出merge模式

该命令将会抛弃合并过程并且尝试重建合并前的状态

```bash
git merge --abort
```



#### 保存提交

最后再重新提交一遍就成功的解决了冲突

<img class="base" src="/../images/git/合并分支_提交冲突文件.png"></img>

