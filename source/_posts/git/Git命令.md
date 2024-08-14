---
title: 【Git】基础命令
date: 2024-08-11 18:55:06
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
// 将本地仓库的<branch_name>分支推送到远程仓库的<branch_name>分支上
git push -u <origin_name> <branch_name>
// 将远程仓库的branch_name拉取到本地工作区
git pull <origin_name> <branch_name>
```

#### 推送

```shell
# 将本地的<branch_name>分支推送到远程的<branch_name>分支上
git push <origin_name> <branch_name>
# 将本地的分支推送到远程分支上
git push <origin_name> <本地分支>:<远程分支>
```

还可以添加`-u`参数设置默认的推送和拉取映射关系
使用这个参数之后可以直接使用`git push`和`git pull`而不用再添加参数

```shell
# 将本地的master分支推送到origin的master分支上，并设置这个为默认的推送和拉取映射
git push -u origin master
# 后面如果需要推送或者拉取可不用携带参数，默认为origin远程的master分支
git push # 将本地的master分支推送到远程的master分支上
git pull # 将远程的master分支拉取到本地的master分支上
```

注意：
经过测试发现携带`-u`参数时使用`master:main`的映射方法，后续使用`git push`无法成功的将本地的master分支推送到远程的main上
也就是说，如果使用了`-u`参数，那么需要推送到的远程分支名必须与本地分支名一致

#### 拉取

##### 将远程分支上的内容和到本地分支

有两种方法`git pull`和`git fetch`
两者的关系是：`git pull`是执行了`git fetch`和`git merge`两个操作

##### pull命令

```shell
# 将远程的<branch_name>分支拉取到本地的<branch_name>分支上
git pull <origin_name> <branch_name>
# 将远程的分支拉取到本地分支上
git pull <origin_name> <远程分支>:<本地分支>
```

可直接使用`git pull <origin_name> <branch_name>`将`<origin_name>/<branch_name>`的内容直接合并到本地

##### fetch命令

```shell
git fetch <origin_name> <branch_name>
git merge FETCH_HEAD
```

1. 使用`git fetch <origin_name> <branch_name>`将`<origin_name>/<branch_name>`的内容保存到`.git/FETCH_HEAD`文件中
2. 使用`git merge FETCH_HEAD`将`FETCH_HEAD`中的信息合并到当前分支

##### 将远程分支拉取到本地作为一个新的分支

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



---

### 仓库文件

#### 获取仓库大小

```shell
git count-objects -vH
```

在使用这个命令之前可以先使用`git gc`优化一下仓库。可以看到`size-pack`参数就是仓库的大小

这个命令是获取当前`仓库文件`的大小的，与你当前`本地文件`的大小不一样

- `仓库文件`：只要上传过的文件，就会计入在里面
- `本地文件`：使用window的资源管理器，所见即所得，没有其他的文件

>  一个特殊的情况是：
>
>  你不小心上传了一个1G的文件夹，现在你想要把他排除在外，使用`git rm --cached logs/`成功排除了这个文件夹，并且以后也都不会再跟踪这个文件夹了。
>
>  但是你在这之前上次的1G大小的文件依然是还存在这个git仓库里的，并不会消失，使用上面的这个命令获取到的文件大小是包含这个`logs/`文件的
>
>  目前没有找到彻底的删除这个1G的文件，然后你又不能回退版本的话，现在只能将你仓库根目录下的`.git`文件删除掉，再从新`git init`初始化一个仓库了。**当然在做这个操作之前，建议先备份一下**



#### 列出仓库所有文件

```shell
git ls-files
```

这个命令有很多参数，具体可以使用`git ls-files --help`打开本地的帮助文档查看

```shell
git ls-files -z | xargs -0 du -hc | grep total$
```

可以列出所有文件大小。

- `-z`：\0行终止输出，不引用文件名的输出格式，具体可看本地帮助文档
- `-0`：防止文件中有空格
- `-h`：以人类可读的格式显示文件和目录的大小
- `-c`：在最后一行显示总大小，包括所有指定目录的大小
- `total$`：正则匹配

<img class="base" src="/../images/git/git命令/列出仓库所有文件.png"></img>



---

### 其他

#### 记住账号密码

在linxu中每次都要输入账号密码，使用此命令后，push的时候再输入一次密码就不用再输入了

```shell
git config --global credential.helper store
```

#### 中文为ASCII码

默认情况下git中文显示为ASCII码，使用该命令之后能正常显示中文

```shell
git config --global core.quotepath false
```







<center class="moderate">持续更新</center>