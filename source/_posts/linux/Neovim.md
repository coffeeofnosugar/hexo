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

将[plug.vim](https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim)文件放在以下路径

windows: `./nvim-win64/config/nvim-data/site/autoload/`

linux: `./nvim-linux64/config/nvim/site/autoload/`

安装方法

- 在nvim窗口下输入`:PlugInstall`
- 在linux终端输入`nvim +PlugInstall +qall`

第一种安装方法可能会因为网络的原因安装失败，这时就可以使用第二种方法

如果出现Finishing ... Done! 和 Already installed 就说明安装成功了

<img src="/../images/linux/nvim/插件.png"></img>

后面安装的插件位置会放在~/vim/plugged文件夹中

[插件网站](https://vimawesome.com/)



---

### 我的配置

#### 热键

| imap <key1>  <key2> | 将输入模式的key1映射到key2（key1和key2都有key2的功能） |
| ------------------- | ------------------------------------------------------ |
| nmap  <key1> <key2> | 将命令模式的key1映射到key2上                           |

#### 特殊键位

| <A-q>   | alt + q  |
| ------- | -------- |
| <C-q>   | Ctrl + q |
| <Esc>   | esc键    |
| <space> | 空格     |

#### 其他设置

| set number | 显示行号(或者set nu) |
| ---------- | -------------------- |
|            |                      |



```shell
" 基础键位映射
imap jk <Esc>
nmap <space> :

" 显示相对行
set relativenumber
set number

" /的搜索忽略大小写
set ignorecase


call plug#begin()

Plug 'scrooloose/nerdtree'
Plug 'rkulla/pydiction'

call plug#end()




" nerdtree插件绑定
" 使用ctrl+e打开关闭
map <silent> <C-e> :NERDTreeToggle<CR>

" 将光标移动到NERDTree中
nnoremap <C-w> <C-w>w

" vim启动时自动显示NERDTree
"auto VimEnter * NERDTree

" 打开vim时如果没有文件自动打开NERDTree
autocmd vimenter * if !argc()|NERDTree|endif

" 当NERTreed为剩下的唯一窗口时自动关闭
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

" 设定NERTree视窗大小
"let g:NERDTreeWinSize=30

" 修改树的显示图标
let g:NERDTreeDirArrowExpandable = '+'
let g:NERDTreeDirArrowCollapsible = '-'

" 隐藏文件
let NERDTreeIgnore = ['\.pyc$', '__pycache__']

" 是否显示行号
"let g:NERDTreeShowLineNumbers=1

" 是否显示隐藏文件  NERDTree自带的快捷键Ctrl+I，大写I
let g:NERDTreeHidden=0



" pydiction插件   python补全
filetype plugin on
let g:pydiction_location = '$XDG_CONFIG_HOME\\nvim-data\\plugged\\pydiction\\complete-dict'


```

