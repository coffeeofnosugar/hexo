---
title: 【Python】【魔法方法】【装饰器】【上下文管理器】contextlib模块
date: 2023-08-12 15:17:06
tags:
  - Python
  - 魔法方法
---

### 装饰器

 装饰器可以灵活的控制两个函数的执行顺序

#### 无返回值

```python
def sum(func):
    print(1)
    func()
    print(3)
    
@sum
def take():
    print(2)
```

输出结果

```bas
1
2
3
```

#### 有返回值

```python
def outer(func):
    print("outer")            # ----------1
    def wrapper(x, y):        # ----------3
        print("wrapper")      # ----------4
        res = func(x, y)      # ----------5
        return res            # ----------9
    return wrapper            # ----------2


@outer
def inner(x, y):              # ----------6
    print("inner")            # ----------7
    return x+y                # ----------8


print(inner(1,2))
```

输出结果

```bash
outer
wrapper
inner
3
```

---



### 上下文管理器

在 Python 中，上下文管理器常常与 `with` 语句一起使用。`with` 语句会在代码块进入时调用上下文管理器的 `__enter__()` 方法，而在代码块退出时会调用上下文管理器的 `__exit__()` 方法。这种机制确保了资源在适当的时候被初始化和清理。

最基础的上下管理器：

```python
with open("a.txt", 'r') as file:
    file.read()
```

自己定义一个上下文管理器

```python
class MyContext:
    def __enter__(self):
        print("Entering the context")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        exc_type: 异常类型，如果没有异常则为None
        exc_value: 异常值，如果没有异常则为None
        traceback: 追溯信息，如果没有异常则为None
        """
        print("Exiting the context")
        if exc_type is not None:
            print(f"An exception of type {exc_type} occurred with value {exc_value}")
        return False  # Return True if you want to suppress the exception

# 使用with语句创建上下文管理器
with MyContext() as context:
    print("Inside the context")

print("Outside the context")
```

输出

```bash
Entering the context
Inside the context
Exiting the context
Outside the context
```

---



### contextlib模块

#### 基础用法

上面我们自定义上下文管理器确实很方便，但是Python标准库还提供了更加易用的上下文管理器工具模块contextlib，它是通过生成器实现的，我们不需要再创建类以及`__enter__`和`__exit__`这两个特俗的方法：

```python
from contextlib import contextmanager

@contextmanager
def make_open_context(filename, mode):
    fp = open(filename, mode)
    try:
        yield fp
    finally:
        fp.close()

with make_open_context('/tmp/a.txt', 'a') as file_obj:
    file_obj.write("hello carson666")
```

在上文中，`yield`关键词把上下文分割成两部分：

- `yiled`之前就是`__enter__`中的代码块
- `yield`之后就是`__exit__`中的代码块

`yeild`生成的值会绑定到`with`语句的`as`子句中的变量。例如上面的例子中`yield`生成的值是文件句柄对象fp，在下面的with语句中，会将`fp`和`file_obj`绑定到一起，也就是说`file_obj`此时就是一个文件句柄对象，那么它就可以操作文件了，因此就可以调用`file_obj.write("hello world")`

另外要注意的是，如果`yield`没有生成值，那么在`with`语句中就不需要写`as`子句了

#### 将普通的类变为上下文管理器类

```python
from contextlib import contextmanager

class MyResource:
    def query(self):
        print("query data")

@contextmanager
def make_myresource():
    print("connect to resource")
    yield MyResource()
    print("connect to resource")

with make_myresource() as r:
    r.query()
```

输出

```bash
connect to resource
quert data
connect to resource
```
