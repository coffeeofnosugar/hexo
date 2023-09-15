---
title: 【Git】基础命令
date: 2023-08-12 11:17:06
tags: Git
---

<link rel="stylesheet" href="/../css/center.css">
<link rel="stylesheet" href="/../css/images.css">

### 基础结构

#### 文件状态

<img class="base" src="/../images/git/基础结构.png"></img>

1. `Changes to be committed`

   文件已经被`git add <file>`存放在暂存区，现在有两条路可以走

   - 提交：使用`git commit -m ""`提交
   - 恢复：使用`git restore --staged <file>`或`git reset <file>`将文件复原到工作区，文件修改的内容会保留
   
2. `Changes not staged for commit`

   文件被修改，但是还为被`git add <file>`

   - 提交到暂存区：使用`git add <file>`
   - 恢复：使用`git restore <file>`或`git checkout <file>`将文件的内容恢复成上一次提交的内容

3. `Untracked files`

   新建的文件，还未被跟踪。这种状态的文件可以使用`.gitignore`文件取消跟踪
   
   - 使用`git add <file>`跟踪文件
   - 使用`.gitignore`屏蔽文件
   - 直接删除文件




---

### Git远程命令

#### 基础命令

```bash
// 查看绑定了哪些远程仓库
git remote -v
// 删除远程的绑定
git remote remove <name>
// 将本地仓库的内容推送到远程仓库的branch_name分支上
git push -u <origin_name> <branch_name>
// 将远程仓库的branch_name拉取到本地工作区
git pull <origin_name> <branch_name>
```

#### 将远程分支上的内容和到本地分支

有两种方法`git pull`和`git fetch`，但其实`git pull`是执行了`git fetch`和`git merge`两个操作

##### `git pull <origin_name> <branch_name>`命令

可直接使用`git pull <origin_name> <branch_name>`将`<origin_name>/<branch_name>`的内容直接合并到本地

##### `git fetch <origin_name> <branch_name>`命令

1. 使用`git fetch <origin_name> <branch_name>`将`<origin_name>/<branch_name>`的内容保存到`.git/FETCH_HEAD`文件中
2. 使用`git merge FETCH_HEAD`将`FETCH_HEAD`中的信息合并到当前分支、

#### 将远程分支拉取到本地作为一个新的分支

`git checkout -b <new_local_branch> <origin/remote_banch_name>`

在本地创建一个`<new_local_branch>`分支并将`<origin/remote_banch_name>`



---

### 查看log

```shell
# 查看所有分支的提交记录之间的关系(以一行显示)
git log --oneline --graph --all
# 查看每个提交记录修改了哪些文件
git log --stat
# 查看每个提交记录具体的修改内容
git log -p
# 指定显示多少条日志
git log -2
# 指定跳过多少条日志
git log --skip=3
```











<center class="moderate">持续更新</center>