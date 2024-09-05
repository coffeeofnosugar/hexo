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

一般要使用这个命令是因为遇到了冲突，详细处理方法可以查看另一篇文章[【Git】合并分支及如何解决冲突](https://www.coffeeofnosugar.top/2023/09/15/git-Git%E5%90%88%E5%B9%B6%E5%88%86%E6%94%AF%E5%8F%8A%E5%A6%82%E4%BD%95%E8%A7%A3%E5%86%B3%E5%86%B2%E7%AA%81/)



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

### 记住账号密码

在linxu中每次都要输入账号密码，使用此命令后，push的时候再输入一次密码就不用再输入了

```shell
git config --global credential.helper store
```



---

### 中文为ASCII码

默认情况下git中文显示为ASCII码，使用该命令之后能正常显示中文

```shell
git config --global core.quotepath false
```



---

### CRLF will be replaced by LF the next time Git touches it

这个警告提示的意思是，Git 在下次处理文件（例如提交或检出）时，会将文件中的换行符从 CRLF转换为 LF

#### 背景

Git 对不同操作系统的换行符处理有不同的默认设置。通常，Git 会尝试在不同操作系统之间处理换行符的差异。例如：

- **Windows** 使用 CRLF 作为换行符。
- **Unix/Linux/macOS** 使用 LF 作为换行符。

#### 解决方案

1. **保持默认行为**： 如果你不介意这种转换行为，可以忽略这个警告。Git 会在提交时自动处理换行符。

2. **设置 Git 配置**： 你可以通过全局 Git 配置或者设置 `.gitattributes` 文件来控制换行符的处理方式。

**全局Git配置**：在`git shell`上执行<font color="DarkGray">（使用了这个就不用配置`.gitattributes`文件了）</font>

```bash
git config --global core.autocrlf true  # Windows 用户推荐
```

**配置 `.gitattributes` 文件**: 在仓库根目录下创建或编辑 `.gitattributes` 文件，添加以下规则来强制 Git 使用一致的换行符：<font color="DarkGray">（这个配置会覆盖全局设置）</font>

```gitattributes
# 强制所有文本文件使用 CRLF 作为换行符
* text=auto eol=crlf
```


3. **手动转换换行符**: 如果你需要手动处理换行符，可以使用文本编辑器或命令行工具来转换文件的换行符。

```bash
sed -i 's/\r$//' path/to/file.text
```



#### 补救措施

如果之前已经提交过文件了，可以按照以下步骤重新设置文件的换行符

1. 配置`.gitattributes`文件

   ```gitattributes
   # 强制所有文本文件使用 LF 作为换行符
   * text=auto eol=crlf
   ```

2. 删除Git缓存文件

   ```bash
   git rm --cached -r .
   ```

   这个命令会将所有已跟踪的文件从 Git 的暂存区中移除，但不会删除工作目录中的文件。此时，Git 会认为这些文件已被删除。

3. 重新添加所有文件到暂存区并提交更改

   ```bash
   git add .		# 此时可能依然还会报警告，但是不要紧。我们只要存储一次，修改文件在git中的规则之后，下次就不会有这个警告了
   git commit -m "Normalize line endings using CRLF"
   ```

   此时，Git 会根据 `.gitattributes` 文件中指定的换行符规则重新处理这些文件，并将它们添加回暂存区。

4. 验证更改

   ```bash
   git ls-files --eol
   ```

   如果输出的内容是，以下内容就没问题

   ```bash
   i/lf    w/crlf  attr/text=auto eol=crlf .gitattributes
   i/lf    w/crlf  attr/text=auto eol=crlf tset.text
   ```

   - `i/lf`：当前工作副本中的换行符类型<font color="DarkGray">因为使用的是git bash，是Unix，所以工作副本里是lf</font>
   - `w/crlf`： Git 将在下次检出（checkout）或其他操作时将会使用的换行符类型
   - `attr/text=auto eol=crlf`：这是 `.gitattributes` 文件中的设置

   也可以将文件使用`NotePad++`或`rider`等编辑器打开，查看右下角的编码格式

#### 完全消除警告

经过测试发现，在创建Unity的C#脚本的时候`.cs`文件默认是`crlf`，`.meta`文件使用的`lf`。

所以只要你启用了Git全局配置的自动转换，或则在`.gitattributes`中指定了规则，你都无法完全避免这个警告。

**唯一能完全取消这个警告的方法是：不再规范所有文件的换行规则**

具体的做法就是：

1. `git config --global core.autocrlf false`：取消自动转换
2. 在`.gitattributes`注释掉换行规则

这样才能完全让这个警告消失在你的视野中

但正如“有得便有失”，你眼睛不会被脏了，但是代价是什么呢？

> <font color="red">注意：</font>
>
> 不再规范所有文件的换行规则后
>
> - 跨平台使用仓库，会影响文件的内容，从而影响版本控制和合并
> - 多人员开发时，没有规范换行规则也会影响文件内容，从而影响版本控制
>
> **所以只有在个人独自开发，且没有多平台需求的开发项目才能完全避免这个警告。**























<center class="moderate">持续更新</center>