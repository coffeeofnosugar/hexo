---
title: 【Git】忽略文件
date: 2023-08-12 10:37:06
tags: Git
---

## 忽略文件

### .gitignore文件

.gitignore文件只能忽略未跟踪状态的文件，如果已经被跟踪了，可以使用下面的两种方法

---



### git rm --cached \<file>

如果远程仓库已经有了logs文件夹，使用三步完成

1. 使用命令删除文件的跟踪状态 `git rm --cached logs/`
2. 此时本地工作区修改还在，需要更新一下/gitignore文件
3. 最后使用命令删除远程仓库对应的文件`git add . && git commit -m "xx" && git push`

---



### skip-worktree和assume-unchanged

#### skip-worktree

skip-worktree可以实现修改本地文件不会被提交，但又可以拉取最新更改需求。适用于一些不经常变动，但是必须本地化设置的文件

```shell
// 添加忽略文件
git update-index --skip-worktree <file>
// 取消忽略
git update-index --no-skip-worktree <file>
// 查看skip-worktree列表
git ls-files -v | grep '^S\'
```

#### assume-unchanged

该命令只是假设文件没有发生变动，使用reset时会将文件修改回去。当远程仓库相应的文件被修改时，pull更新之后，--assume-unchanged会被清楚

```shell
// 添加忽略文件
git update-index --assume-unchanged <file>
// 取消忽略
git update-index --no-assume-unchanged <file>
// 查看忽略了哪些文件
git ls-files -v | grep '^h\'
```

参考

[一文带你彻底搞懂Git！](https://zhuanlan.zhihu.com/p/559692211)