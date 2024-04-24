---
title: 【lua】lua学习笔记
date: 2024-04-25 03:29:06
tags: lua
---

### 安装

1. 下载[lua环境](https://luabinaries.sourceforge.net/download.html)
2. 将文件解压到任意路径下
3. 将2中的路径设置为电脑的全局变量

### 数据类型

| 数据类型 | 描述                                                         |
| -------- | ------------------------------------------------------------ |
| nil      | 无效值                                                       |
| boolean  | false和true                                                  |
| number   | 双精度类型的实浮点数                                         |
| string   | 字符串类型，使用单引号或双引号表示                           |
| function | 由C或lua编写的函数                                           |
| userdata | 表示任意存储在变量中的C的数据结构                            |
| thread   | 表示执行的独立线路，用于执行协同程序                         |
| table    | Lua中的表(table)其实是一个"关联数组"(associative arrays)，数组的索引可以是数字、字符串或表类型。在 Lua 里，table 的创建是通过"构造表达式"来完成，最简单构造表达式是{}，用来创建一个空表。 |

注：在lua中只有nil表示false，0表示true
