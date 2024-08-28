---
title: 【Unity】【C#】CSharp小技巧
date: 2024-08-11 05:28:06
updated: 2024-08-28 11:27:38
tags:
  - Unity
  - CSharp
---

标题虽然是小技巧，但本篇文章里还是记录了一些常用的功能，**本文章的主要目的是方便日后快速查找**

## C#

{% note default %}

### 访问权限

{% endnote %}

#### 私有化构造函数

单例类，是不需要外界实例化的，可以将构造函数私有化，外界就无法实例化了。

```C#
class Manager
{
    public static Manager Instance = new Manager();		// 单例类
    private Manager() { }								// 私有化构造函数
}
```

#### 接口封装

不希望外界访问这个接口里所有的方法时，可以显示实现接口

```c#
public interface IInterface
{
    void Add();
    void Remove();
    int Get();
}
```

```c#
class ReadOnlyClass : IInterface						// 创建一个只能读取，不能更改内容的类
{
    void IInterface.Add()													// 显示接口实现，外界无法访问
    {
        throw new NotSupportedException("Readonly Not Supported Add");		// 就算访问了，也会抛异常
    }

    void IInterface.Remove()												// 显示接口实现，外界无法访问
    {
        throw new NotSupportedException("Readonly Not Supported Remove");	// 就算访问了，也会抛异常
    }

    public int Get()					// 正常访问Get()方法
    {
        return 1;
    }
}
```
`ReadOnlyDictionary<TKey, TValue>()`、`ReadOnlyList<>`、`ReadOnlyCollection<>`、`ReadOnlySet<>`都是使用显示实现接口的方法隐藏了修改的方法，使外界只能读取，不能修改

完整使用方法：

 ```C#
 class Manager
 {
     private Dictionary<string, string> _uiStack;
     public ReadOnlyDictionary<string, string> UIStack { get; }		// 注意这里没有使用set，完全杜绝了修改的可能
     public Manager()
     {
         UIStack = new ReadOnlyDictionary<string, string>(_uiStack);
     }
 }
 ```

> 拓展：
>
> `{ get; private set; }`：在类内部还能重新setter
>
> `{ get; }`：只能在构造函数中setter







---

{% note default %}

### 列表

{% endnote %}

创建一个按照特定规则排列的列表：

例如，实例化一些`Human`，并且将他们按照`age`从大到小的方式放置一个列表中

```c#
public interface IAnimal
{
    public int age { get; set; }
    public string name { get; set; }
}
public class Human : IAnimal
{
    public int age { get; set; }
    public string name { get; set; }

    public Human(int age, string name)
    {
        this.age = age;
        this.name = name;
    }
}
```

定义一个单例泛型类，用来做比较

```C#
public class ReverseComparer<T> : IComparer<T>
{
    public static readonly ReverseComparer<T> Instance = new ReverseComparer<T>();	// 饿汉单例
    private ReverseComparer() { }				// 私有构造函数，不需要用户创建实例
    public int Compare(T x, T y) => Comparer<T>.Default.Compare(y, x);	// 实现接口，定义比较方法，注意参数换位置了
}			// 如果想要从小到大排列，再换回来就好了
```

```C#
public class HumanSelector : SortedList<int, IAnimal>		// 继承`SortedList<int, IAnimal>`基类
{
   public HumanSelector() : base(ReverseComparer<int>.Instance) {}	// 构造函数，并将参数传递给基类的构造函数
   public void Add<T>(T man)					// 定义了一个泛型方法
       where T : IAnimal						// 这个泛型类必须是来自IAnimal接口的
       => Add(man.age, man);					// 调用了基类的Add方法
}
```

使用：

```C#
Human A = new Human(20, "A");
Human B = new Human(25, "B");
Human C = new Human(30, "C");
HumanSelector humanSelector = new HumanSelector();		// 实例化排序列表
humanSelector.Add(C);
humanSelector.Add(A);
humanSelector.Add(B);
humanSelector.ToList().ForEach(man => { Console.WriteLine($"{man.Key}, {man.Value.name}"); });

// 30, C
// 25, B
// 20, A
```

这样，我们就将排序封装起来了，使用者只需要使用`Add`将元素添加到排序列表中就OK了









---

{% note %}

### 字段与属性

{% endnote default %}

#### 索引器

总得来说大致有三种用法

1. 最普通的，针对字段复制了一个属性供外界使用，每次访问都会创建一个值类型的副本。

```C#
private int _count;							// 字段：内部使用
public int Count							// 属性：外部可读可写
{
    get => _count;
    set => _count = value / 2;				// 可自定义读写需求
}
```

```c#
private int _length;
public int Length => _length;					// 属性：公共只读
```

```C#
public static int TotalCount { get; set; }		// 属性：可读可写，这种方式实际上也隐式的创建了一个字段，如下图
```

<img class="half" src="/../images/unity/CSharp小技巧/属性和字段.png"></img>



2. 使用了`ref`修饰，使`Run`实际上是直接访问的`_run`这个字段，减少了一个复制的过程，提高性能

```c#
[SerializeField]
private bool _run;							// 内部使用
public ref bool Run => ref _run;		// 外部使用，这里实际上是直接访问的_run这个字段
```



3. 可以让类像列表一样访问

```c#
public string this[int index]
{
    get => _items[index];
    set => _items[index] = value;
}
```

甚至还可以将字典改成与python一样的用法：<font color="DarkGray">不过不推荐这种用法</font>

```C#
public class CustomizeDict
{
    private Dictionary<string, string> _data = new Dictionary<string, string>();
    public object this[string key]
    {
        get => _data[key];
        set
        {
            if (_data.ContainsKey(key))
                _data[key] = value.ToString();
            else
                _data.Add(key, value.ToString());
            UpdateContent();
        }
    }
}

CustomizeDict["speed"] = 500;
```





#### `default`

常用`default`能使代码排版更好看，可以省去写判断表达式

值类型

```C#
int number = defaule;   // 默认值为0
double amount = default；   // 默认值为0
bool flag = default;    // 默认值为false
```

引用类型

```C#
string text = default;		// 默认值为null
List<int> numbers = defalut;   // 默认值为null
```











---

{% note default %}

### 字符串、数组切片


{% endnote %}

C#在8.0后字符串和数组可以像`python`一样使用切片，时代码变的即简单又美观

<font color="DarkGray">值得注意的是列表不能使用这个小技巧</font>

示例：

<img class="half" src="/../images/unity/CSharp小技巧/HelloWorld.png"></img>

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

{% note default %}

### 简写判断语句

{% endnote %}

**这里面的所有简写rider都会提示，部分简写不建议使用，大大提高的代码的阅读效率**

#### 一个数介于两个数之间

```C#
var ran = new Random();
int i = ran.Next(20);	// 在0-20之间随机选一个数

if (i is < 10 and > 0)
    Console.WriteLine("i介于0和10之间");
```

> 值得注意一点的是，这个判断的两个数必须是常量值
>
> 如果是`list.Count`，这里就用不了了

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

#### 赋值判断

- `A |= B`：位或，左右两边的值进行位或，并将结果赋值给左边的变量。`bool a |= 1 < 10;` 结果为`True`。<font color="DarkGray">位或：`A |= B`，如果B是true，那么A就是true；否则A的值不变</font>
- `result = A ?? B`：如果A是null，返回B；否则返回A
- `result ??= new List<int>()`：如果result是空，就进行复制操作；否则不做任何操作

- `result = A is { age: 20 }`：等价`result = A != null && A.age == 20`












---

{% note default %}

### 格式化字符串


{% endnote %}

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









## Unity

{% note default %}

### 属性


{% endnote %}

##### 序列化

- `SerializeReference`：使Inspector窗口能序列化接口或抽象类，序列化的时候就已经实例化了，可以不需要使用`new()`实例化







---

{% note default %}

### 内置方法


{% endnote %}

- `void OnValidate()`：这个方法会将用户在UnityEditor上的操作实时映射到脚本上













