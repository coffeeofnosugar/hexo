---
title: 【Unity】【C#】CSharp小技巧
date: 2024-08-11 05:28:06
tags:
  - Unity
  - CSharp
---

标题虽然是小技巧，但本篇文章里还是记录了一些常用的功能，**本文章的主要目的是方便日后快速查找**



### 字符串、数组切片

C#在8.0后字符串和数组可以像`python`一样使用切片，时代码变的即简单又美观

<font color="DarkGray">值得注意的是列表不能使用这个小技巧</font>

示例：

<img class="half" src="/../images/unity/CSharp小技巧/HellowWorld.png"></img>

```C#
var str = @"HelloWorld";

Console.WriteLine(str[1..5]);			// "ello"

Console.WriteLine(str[^1]);				// "d"
Console.WriteLine(str[..^0]);			// "HelloWorld"

Console.WriteLine(str[6..^2]);			// "or"
Console.WriteLine(str[^5..^1]);			// "Worl"
Console.WriteLine(str[^7..8]);			// "loWor"
```

- 这里的`^`和`python`里的`-`一样：反着数，`^1`表示最后一个字符`d`，`^5`表示倒数第五个字符`W`
- 左闭又开，包含第一个参数，不包含第二个参数



---

### 简写判断语句

#### 一个数介于两个数之间

```C#
var ran = new Random();
int i = ran.Next(20);	// 在0-20之间随机选一个数

if (i is < 10 and > 0)
    Console.WriteLine("i介于0和10之间");
```

#### 循环判断

为方便理解我先写成这样，解释一下每个方法的含义

```C#
var list = new List<int>() { 5, 2, 7, 1, 9, 4 };		// 定义一个int列表
IEnumerable<int> temp = list.Where(i => i > 3);			// 获取这个列表中大于3的元素的IEnumerable<int>枚举
list = temp.ToList();									// 将IEnumerable<int>枚举转换成列表
list.ForEach(Console.WriteLine);						// 使用方法组的方式逐个打印结果
```

可简写成如下

```C#
var list = new List<int>() { 5, 2, 7, 1, 9, 4 };
foreach (var j in list.Where(i => i > 3))		// 提一嘴，里的i和j其实是分隔开的，并不会相互影响，j可以写成i
{
    Console.WriteLine(j);
}
```

> 老实做法：
>
> ```c#
> var list = new List<int>() { 5, 2, 7, 1, 9, 4 };
> foreach (var i in list)
> {
>     if (i > 3)
>         Console.WriteLine(i);
> }
> ```
>
> 这一样看上面的方法是不是即简洁又好看
>
> 但其实这些都是rider编辑器会提示或者直接帮我们转的，只要别说看不懂是什么意思就行了






---

### 格式化字符串

#### 用法

虽然这个应该是很常用的，但还是提一下

有两种写法，其输出结果是一样的

```C#
int count = 100;
Console.WriteLine("我今天吃了{0}顿", count)
Console.WriteLine($"我今天吃了{count}顿")
```

> 第二种方法的性能要比第一种好 
>
> 但是第一种情况在一些特殊的情况下使用有奇效，比如多语言设置、字符串替换等功能
>
> 具体可以看[C#中字符串类的一些实用技巧及新手常犯错误](https://www.bilibili.com/video/BV1mx4y1x7JR?t=1584.4)这个大佬的

以上用的算的比较多的，所以不是今天的重点，今天的重点在格式化插值和格式化输出

```C#
double i = 32.53728012341241562;

Console.WriteLine($"我的资产为{i, 10:F4}为所欲为");		// "我的资产为   32.5373为所欲为"
```

- `10`表示占位10个位置，当位置不够的时候在前面用空格补充
- `F4`表示保留4位小数，`F`不区分大小写

除了`F`外还有其他很多格式：

#### 数字格式

数字格式都不区分大小写

- `F`：Fiexd-point格式。显示小数后几位。`$"{1234567.89:F2}"` => `1234567.89`
- `C`：货币格式。显示货币符号和千位分隔符。`$"{1234.56:c}"` => `￥1,234.56`
- `E`：科学计数法格式。显示非常大或非常小的数字。`$"{1231421432:e3}"` => `1.231e+009`
- `N`：与`F`类似，但是`N`能显示整数上的千位分隔符。`$"{21432.537280:n3}"` => `21,432.537`
- `G`：自动选择合适的格式。
- `P`：百分比格式。将数值乘以100，并在结果后面加上百分号。`$"{0.12345:p2}"` => `12.35%`
- `R`：常规格式。不带任何格式的方式显示数字，但保留足够的精度（怎么保留没有仔细研究，简单测试了几下，没有找出规律）

#### 日期时间格式

与数字格式不同，日期时间格式需要区分大小写

>  **注意：码代码的时候一定要拼写正确，是`DateTime`不是`DataTime`**
>
> 年月日的排布`DateTime`会自动更具文化设置

先看看普通的格式长什么样`DateTime.Now` => `2024/8/11 4:50:47`

- `d`：短日期格式。`$"{date:d}"` => `2024/8/11`
- `D`：长日期格式。`$"{date:D}"` => `2024年8月11日`
- `t`：短时间格式。`$"{date:t}"` => `4:57`
- `T`：长时间格式。`$"{date:T}"` => `4:58:41`
- `f`：(短)完整日期和时间。`$"{date:f}"` => `2024年8月11日 4:59`

- `F`：(长)完整日期和时间。`$"{date:F}"` => `2024年8月11日 5:00:45`
- `M`或`m`：月日格式。`$"{date:m}"` => `8月11日`
- `Y`或`y`：年月格式。`$"{date:m}"` => `2024年8月`

另外还有十分强大的**自定义**格式化

```C#
DateTime date = DateTime.Now;
Console.WriteLine($"{date:yyyy年mm月dd日 hh:mm:ss tt zzz}");
```

输出：

```shell
2024年05月11日 05:05:09 上午 +08:00
```





---













