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

##### 默认配置文件路径：

```bash
# 创建配置文件夹
mkdir ~/.config/nvim
# 创建配置文件
nvim ~/.config/nvim/init.vim
```

##### 自定义配置文件的路径：

1. 创建配置文件

```bash
cd /usr/local/nvim-linux64
mkdir ./config
mkdir ./config/nvim
# 创建配置文件
nvim ./config/nvim/init.vim
```

<img src="/../images/linux/nvim/配置文件1.png"></img>

2. `nvim /etc/profile`修改环境变量

```bash
# nvim配置文件
export XDG_CONFIG_HOME=/usr/local/nvim-linux64/config
export XDG_DATA_HOME=/usr/local/nvim-linux64/config
```

<img src="/../images/linux/nvim/配置文件2.png"></img>

3. 重载配置文件

```bash
source /etc/profile
```

#### 基础配置

```bash
" 基础键位映射
imap jk <Esc>
nmap <space> :

" 显示相对行
set relativenumber
set number
```

#### 安装vim-plug插件管理

前面不是命名了全局变量`XDG_DATA_HOME`吗，这个时候就用上了

创建路径`/usr/local/nvim-linux64/config/nvim/site/autoload/`

并将`plug.vim`文件放在这个路径下

[Download plug.vim](https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim)

---



### 我的配置

```shell
" 基础键位映射
imap jk <Esc>
nmap <space> :

" 显示相对行
set relativenumber
set number

" nerdtree插件绑定
map <silent> <C-e> :NERDTreeToggle<CR>

" python补全
filetype plugin on
let g:pydiction_location = '$XDG_CONFIG_HOME\\nvim-data\\plugged\\pydiction\\complete-dict'


call plug#begin()

Plug 'scrooloose/nerdtree'
Plug 'rkulla/pydiction'

call plug#end()
```

