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



---

#### table表

- 类似于python中的集合

- 索引从1开始
- *当我们获取 table 的长度的时候无论是使用* `#` 还是` table.getn` 其都会在索引中断的地方停止计数，而导致无法正确取得 table 的长度。如`tbl = {[1] = 2, [2] = 6, [3] = 34, [26] =5}`的长度为3。

表的常用方法：

| 方法                                      | 用途                                          |
| ----------------------------------------- | --------------------------------------------- |
| `table.concat(table[,sep[,start[,end]]])` | 将表从start到end以sep分隔符隔开，使用时需注意 |
| `table.insert(table,[pos,]value)`         | 在pos位置插入元素，pos参数可选，默认尾部插入  |
| `table.remove(table[,pos])`               | 移除元素，pos参数可选，默认尾部 元素          |
| `table.sort(table[,comp])`                | 将表升序排序                                  |

>  注意：
>
> 在使用`table.concat`方法时，表需要有正确的格式才能正确显示。
>
> 错误的格式：
>
> ```lua
> -- 错误格式一：跳序号
> tlb = {[1] = "aa", [2] = "bb", [3] = "cc", [10] = "dd"}
> 
> print(table.concat(tlb, ","))		-- 输出aa,bb,cc
> 
> -- 错误格式二：序号为非数字
> tlb = {[1] = "aa", foo = "bb", [3] = "cc"}
> 
> print(table.concat(tlb, ","))		-- 输出aa
> ```



---

#### 模块与包

创建一个模块就是创建一个table，将需要导出的常量、函数放入其中

##### 创建模块

```lua
-- 创建一个module.lua的文件
module = {}
module.name = "模块"
module.version = "1.0.0"

function module.init()
    print("模块初始化")
end

local function localfunc()
    print("私有化函数")
end

function module.test()
    print("访问私有化函数")
    localfunc()
end
```



##### 访问模块

```lua
-- 创建一个test.lua的文件
-- 在引用module.lua文件前，需要添加相对路径
package.path = package.path .. ";module.lua"

require("module.lua")

module.init()
```



---

#### Metatable元表

设置元表

```lua
-- 方法一
mytable = {}
mymetatable = {}
setmetatable(mytable, mymetatable)

-- 方法二
mytable = setmetatable({}, {})
```

返回元表

```lua
getmetatable(mytable)
```



##### __index元方法

当你通过键来访问 table 的时候，如果这个键没有值，那么Lua就会寻找该table的metatable（假定有metatable）中的__index 键。如果__index包含一个表格，Lua会在表格中查找相应的键。

```lua
other = {foo = 3}

tlb = setmetatable({}, {__index = other})

print(tlb.foo)    -- 输出3
```

__index可以包含一个函数，函数的参数固定为table和键

```lua
tlb = setmetatable({key1 = "value1"}, {
    __index = function(t, k)
    	print("key: " .. k)
    	return "value"
end})

-- 先看本身是否拥有该键，如果有直接返回对应值，如果没有再将table和键传入函数中进行下一步运算，最终结果为返回值
print(tlb.key1)		-- 输出value1
print(tlb.key2)		-- 输出key: key2
					--	  value
```

> 总结：
>
> Lua 查找一个表元素时的规则，其实就是如下 3 个步骤:
>
> - 1.在表中查找，如果找到，返回该元素，找不到则继续
> - 2.判断该表是否有元表，如果没有元表，返回 nil，有元表则继续。
> - 3.判断元表有没有 __index 方法，如果 __index 方法为 nil，则返回 nil；如果 __index 方法是一个表，则重复 1、2、3；如果 __index 方法是一个函数，则返回该函数的返回值。



##### __newindex元方法

当你给表的一个缺少的索引赋值，解释器就会查找__newindex 元方法：如果存在则调用这个函数而不进行赋值操作。

```lua
-- 当__newindex=table时
mymetatable = {key2 = 10}
mytable = setmetatable({key1 = "value1"}, { __newindex = mymetatable })

print(mytable.key1)							-- 输出value1

-- 本表和元表都没有该键：本表为空，元表成功赋值
mytable.newkey = "新值"
print(mytable.newkey,mymetatable.newkey)	-- 输出nil 新值

-- 本表有该键，元表没有：本表成功赋值，元表为空
mytable.key1 = "新值1"
print(mytable.key1,mymetatable.key1)		-- 输出新值1 nil

-- 本表没有该键，元表有：本表为空，元表成功赋值
mytable.key2 = "新值2"
print(mytable.key2,mymetatable.key2)		-- 输出nil 新值2
```

```lua
-- 当__newindex=函数时，将table、键、值代入函数
mytable = setmetatable({key1 = "value1"}, {
    __newindex = function(mytable, key, value)
        rawset(mytable, key, "\""..value.."\"")
    end
})

mytable.key1 = "new value"
mytable.key2 = 4

print(mytable.key1,mytable.key2)			-- 输出new value "4"
```

> 拓展：
>
> `rawset(table, key, value)`方法：在不触发任何元方法的情况下将table[index]设为value（即不受__newindex的影响
>
> `rawget(table, index)`方法：同上，在不触发任何元方法的情况下获取table[index]（即不受__index的影响
>
> ```lua
> local tableA = {}
> local tableB = {NUM = 100}
> local tableC = {}
> 
> setmetatable(tableA, {__index = tableB, __newindex = tableC})
> print(tableA.NUM)				-- 输出100
> print(rawget(tableA,"NUM"))		-- 输出nil
> 
> tableA.NAME = "AA"
> print(tableA,NAME)				-- 输出nil
> print(tableC.NAME)				-- AA
> 
> rawset(tableA, "NAME", "I AM AA")
> print(tableA.NAME)				-- 输出I AM AA
> ```



##### 表的操作符

类似于python的魔法方法

| 模式     | 描述              |
| -------- | ----------------- |
| __add    | 对应的运算符'+'   |
| __sub    | 对应的运算符 '-'  |
| __mul    | 对应的运算符 '*'  |
| __div    | 对应的运算符 '/'  |
| __mod    | 对应的运算符 '%'  |
| __unm    | 对应的运算符 '-'  |
| __concat | 对应的运算符 '..' |
| __eq     | 对应的运算符 '==' |
| __lt     | 对应的运算符 '<'  |
| __le     | 对应的运算符 '<=' |

> 定义表的相加
>
> ```lua
> -- 计算表中最大值，table.maxn在Lua5.2以上版本中已无法使用
> -- 自定义计算表中最大键值函数 table_maxn，即返回表最大键值
> function table_maxn(t)
>     local mn = 0
>     for k, v in pairs(t) do
>         if mn < k then
>             mn = k
>         end
>     end
>     return mn
> end
> 
> -- 两表相加操作
> mytable = setmetatable({ 1, 2, 3 }, {
>   __add = function(mytable, newtable)
>     for i = 1, table_maxn(newtable) do
>       table.insert(mytable, table_maxn(mytable)+1,newtable[i])
>     end
>     return mytable
>   end
> })
> 
> secondtable = {4,5,6}
> 
> mytable = mytable + secondtable
>         for k,v in ipairs(mytable) do
> print(k,v)
> end
> ```

##### __tostring元方法

__tostring元方法用于修改表的输出行为

```lua
mytable = setmetatable({ 10, 20, 30 }, {
  __tostring = function(mytable)
    sum = 0
    for k, v in pairs(mytable) do
                sum = sum + v
        end
    return "表所有元素的和为 " .. sum
  end
})
print(mytable)			-- 输出表所有元素的和为 60
```

