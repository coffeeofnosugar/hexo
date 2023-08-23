---
title: 【Linux】Nvim
date: 2023-08-22 22:42:06
tags: Linux
---

### 安装

#### 下载包体

https://github.com/neovim/neovim/releases

#### 安装

```bash
tar -zxvf neovim-0.8.0.tar.gz
# 解压后就可以直接用了，十分方便
./nvim-linux64/bin/nvim
# 可以将其放在/usr/local下，然后创建软链接
sudo ln -s /usr/local/nvim/bin/nvim /usr/bin/nvim
```

---



### 配置

#### 创建配置文件

默认配置文件位置：

```bash
# 创建配置文件夹
mkdir ~/.config/nvim
# 创建配置文件
nvim ~/.config/nvim/init.vim
```

也可以自定义配置文件的路径

1. 创建配置文件

```bash
cd /usr/local/nvim-linux64
mkdir ./config
mkdir ./config/nvim
# 创建配置文件
nvim ./config/nvim/init.vim
```

<img src="/../images/Linux/nvim/配置文件1.png"></img>

2. `nvim /etc/profile`修改环境变量

```bash
# nvim配置文件
export XDG_CONFIG_HOME=/usr/local/nvim-linux64/config
export XDG_DATA_HOME=/usr/local/nvim-linux64/config
```

<img src="/../images/Linux/nvim/配置文件2.png"></img>

3. 重载配置文件

```bash
source /etc/profile
```

#### 我的配置

```bash
" 基础键位映射
imap jk <Esc>
nmap <space> :

" 显示相对行
set relativenumber
set number
```

