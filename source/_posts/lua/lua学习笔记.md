---
title: 【lua】lua学习笔记
date: 2024-04-25 03:29:06
tags: lua
---

### Lua安装

1. 下载[lua环境](https://luabinaries.sourceforge.net/download.html)
2. 将文件解压到任意路径下
3. 将2中的路径设置为电脑的全局变量



---

### Lua数据类型

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

对table的索引使用方括号`[]`外还可以使用`.`

```lua
tlb = {"aa", "bb", "cc"}
tlb["aa"]
tlb.aa
```



注：

> 在lua中只有nil表示false，0表示true
>
> 在lua中序列号从1开始



---

### Lua变量 

Lua 变量有三种类型：全局变量、局部变量、表中的域
Lua 中的变量全是全局变量，哪怕是语句块或是函数里，除非用 local 显式声明为局部变量
局部变量的作用域为从声明位置开始到所在语句块结束
变量的默认值均为 nil



可以和pytohn一样，赋值时可以一次赋值多个变量

```lua
a, b = 10x, x*x

-- 当变量个数和值个数不一致时
-- 未被赋值的变量会变为nil
a, b, c = 0, 1         --> 0, 1, nil
-- 多余的值会背忽略
a, b = 0, 1, 2         --> 0, 1
```

常用作交换变量，或将函数调用返回给变量

```lua
a, b = b, a
a,b = func()
```



---

### Lua循环

#### `while`循环

```lua
a = 10
while a > 0 do
  print(a)
  a = a - 1
end
```

#### `for`循环

##### 数值for循环

```lua
for var=exp1,exp2,exp3 do  
    <执行体>  
end  
```

var 从 exp1 变化到 exp2，每次变化以 exp3 为步长递增 var，并执行一次 **"执行体"**。exp3 是可选的，如果不指定，默认为1

```lua
for i = 1, 10, 1 do
  print(i)
end
```

##### 泛型for循环

泛型for循环通过一个迭代器函数来遍历所有值，类似于C#中的foreach语句

```lua
--打印数组a的所有值  
a = {"one", "two", "three"}
for i, v in ipairs(a) do
    print(i, v)
end
```

> 拓展：
>
> 将上述的`ipairs`替换成`pairs`是一样的结果，但他们的实现却有些不同
>
> ipairs适用于数组（i估计是integer的意思），pairs适用于对象，因为数组也是对象，所以pairs用于数组也没问题。
>
> 详细可看[Lua的for in和pairs](https://blog.csdn.net/liuyuan185442111/article/details/54144348)

#### `repeat...until`循环

重复执行循环，直到指定的条件为真为止

```lua
a = 10
repeat
  print(a)
  a = a - 1
until a == 0
```



---

### Lua流程控制

```lua
a = 11
if a > 10 then
  print("a大于10")
elseif a == 10 then
  print("a等于10")
else
  print("a小于等于10")
end
```

注：Lua中的0为true



---

### Lua函数

可变参数

```lua
function add(...)
  for index, value in ipairs(...) do
    print(index, value)
  end
end

tlb1 = {"aa", "bb", "cc"}

tlb2 = {"AA", "BB", "CC", "DD"}

add(tlb1)
add(tlb2)
add(111, 222, 333, 444)
```

注：可变参数直接传入值与传入表的用法不一样

- `select("#", ...)`可以用在表和值
- `#...`只能用在表上

```lua
-- 传入表
function f(...)
  print(select("#", ...))		-- 错误用法，返回1
  print(#...)					-- 正确用法，返回3
end

tlb = {"aa", "bb", "cc"}
f(tlb)
```

```lua
-- 传入值
function f(...)
  print(select("#", ...))		-- 正确用法，返回3
  -- print(#...)				-- 错误用法，报错。可使用local tlb = ...，然后再用#tlb获取长度
end

f(0, 1, 2)
```

#### `select()`函数

- `select("#", ...)`返回可变参数的长度
- `select(n, ...)`用于返回从起点n开始到结束为止的所有参数列表
- `a = select(n, ...)`将参数列表索引为n的参数赋值给a

```lua
function f(...)
  print(select("#", ...))		-- 输出6
  print(select(2, ...))			-- 输出1 2 3 4 5
  a = select(2, ...)			-- 将参数列表索引为n的参数赋值给a
  print(a)						-- 输出1
end

f(0, 1, 2, 3, 4, 5)
```

遍历`select(n, ...)`
无法直接使用for循环直接遍历`select(n, ...)`所返回的数据
需要获取到返回数据的长度，然后再通过索引号获取数据中的元素

```lua
function f(...)
  for i = 1, select("#", ...) do
    local a = select(i, ...)
    print(a)
  end
end

f(0, 1, 2, 3, 4, 5)
```

