---
title: 【Unity】UniTask学习笔记
date: 2024-07-05 15:32:06
tags:
  - Unity
---

### 优势

#### 协程

1. 协程是与`MonoBehaviour`绑定的，如果没有继承自`MonoBehaviour`就无法使用
2. 协程会产生很多GC，每次调用 `yield return` 都会创建一个 `IEnumerator` 对象。<font color="DarkGray">如果使用`yield return 0`或`yield return new WaitForSeconds(2f)`还会出现装箱的操作</font>
3. Unity 每帧会检查所有正在运行的协程并执行，频繁的上下文切换可能会影响性能
4. 无法通过`try/catch`捕获异常
5. 协程是跟随UnityObject生命周期的，GameObject被销毁后协程也会停止
6. 停止协程比较麻烦
7. 不支持返回值



#### 原生 `async/await` 

1. 每个 `Task` 都是一个类对象，它在创建时会分配堆内存
2. 无法支持WebGL
3. 在部分情况下无法捕获异常
4. 不支持返回值



#### UniTask

1. UniTask是针对Unity的异步编程，支持WebGL
2. 主要通过结构体来管理异步，避免内存分配和GC压力
3. 轻松捕获异常
4. 便利的停止异步任务
5. 支持返回值



---

### UniTaskTracker

```C#
void start()
{
	ExampleUniTask().Forget();
}
async UniTask ExampleUniTask()
{
    for (int i = 0; i < 100; i++)
    {
        await UniTask.Delay(50);
    }
}
```

<img class="half" src="/../images/unity/UniTask学习笔记/UniTaskTracker-1.png"></img>

<img class="half" src="/../images/unity/UniTask学习笔记/UniTaskTracker-2.png"></img>

如果没有按照正确方式使用`AsyncUniTask`不会消失，例如将上面的代码改成：

```C#
void start()
{
	ExampleUniTask();
}
```

<img class="half" src="/../images/unity/UniTask学习笔记/UniTaskTracker-3.png"></img>

> 正确使用的两种方式：
>
> - 使用`await`修饰：后面的代码会等待执行完毕后再执行
> - 使用`.Forget()`：不会等待，直接执行后面的代码

> Status
>
> - Succeeded：执行完毕
> - Canceled：被`CancellationTokenSource`取消



### `WhenAll`与`WhenAny`

他们两个最主要的区别就是什么时候结束等待，开始执行后面的代码

```c#
await UniTask.WhenAll(
    ExampleUniTask(bar1, 50),
    ExampleUniTask(bar2, 100),
    ExampleUniTask(bar3, 100)
    );
Debug.Log("All tasks completed");
```

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/UniTask学习笔记/WhenAll.png"></img>

<img class="half" src="/../images/unity/UniTask学习笔记/WhenAny-1.png"></img>

{% endgrouppicture %}

>  也可以用来控制取消任务
>
> ```c#
> await UniTask.WhenAny(
>     ExampleUniTask(bar1, cts.Token),
>     ExampleAsync(bar2, cts.Token).AsUniTask(),
>     ExampleCoroutine(bar3).WithCancellation(cts.Token)
>     );
> cts.Cancel();
> Debug.Log("All tasks completed");
> ```
>
> <img class="half" src="/../images/unity/UniTask学习笔记/WhenAny-2.png"></img>



### 使进程跟随GameObject生命周期

就像前面优势说的，UniTask即使在物体被摧毁后也能执行，那么如何控制UniTask跟随GameObject生命周期呢

方法一：

```C#
private async void Start()
{
    var token = this.GetCancellationTokenOnDestroy();

    await ExampleUniTask(bar1, token);
}
```

方法二：

```C#
private CancellationTokenSource _cts = new CancellationTokenSource(); 

private async void Start()
{
    await ExampleUniTask(bar1, _cts.Token);
}
private void OnDestroy()
{
    _cts?.Cancel();
}
```



### 返回值

#### 无返回值

如果不在意返回的内容可以使用`UniTaskVoid`

当然，这样就不能使用`await`修饰了，更不能加入到`WhenAll`或`WhenAny`了

```c#
async UniTaskVoid ExampleUniTask(CancellationToken token)
{
    for (int i = 0; i < 100; i++)
    {
        token.ThrowIfCancellationRequested();
        await UniTask.Delay(50);
        Debug.Log(i);
    }
}
```

#### 有返回值

如果需要返回值，必须使用`await`修饰

```C#
void Start()
{
    var (a, b, c) = await UniTask.WhenAll(
        DelayedValueAsync(1, 5),
        DelayedValueAsync(2, 10),
        DelayedValueAsync(3, 20)
    );
    Debug.Log($"{a}, {b}, {c}");
}

async UniTask<int> DelayedValueAsync(int value, int delayFrames)
{
    await UniTask.DelayFrame(delayFrames);
    await UniTask.Yield(PlayerLoopTiming.FixedUpdate);
    return value * 2;
}
```



---

### 其他

#### 线程

```C#
private async void Start()
{
    Debug.Log($"主线程ID: {Thread.CurrentThread.ManagedThreadId}");
    using (var cts = new CancellationTokenSource())
    {
        ExampleUniTask(bar1, cts.Token).Forget();
        ExampleAsync(bar2, cts.Token);
        StartCoroutine(ExampleCoroutine(bar3));
    }
}

async UniTask ExampleUniTask(HealthScrollbar healthScrollbar, CancellationToken token)
{
    Debug.Log($"ExampleUniTask线程ID: {Thread.CurrentThread.ManagedThreadId}");
    for (int i = 0; i < 100; i++)
    {
        token.ThrowIfCancellationRequested();
        await UniTask.Delay(50, cancellationToken: token);
        healthScrollbar.Number++;
    }
}

async Task ExampleAsync(HealthScrollbar healthScrollbar, CancellationToken token)
{
    Debug.Log($"ExampleAsync线程ID: {Thread.CurrentThread.ManagedThreadId}");
    for (int i = 0; i < 100; i++)
    {
        token.ThrowIfCancellationRequested();
        await Task.Delay(50, token);
        healthScrollbar.Number++;
    }
}

IEnumerator ExampleCoroutine(HealthScrollbar healthScrollbar, CancellationToken token)
{
    Debug.Log($"ExampleCoroutine线程ID: {System.Threading.Thread.CurrentThread.ManagedThreadId}");
    for (int i = 0; i < 100; i++)
    {
        yield return new WaitForSeconds(0.05f);
        healthScrollbar.Number++;
    }
}
```

<img class="half" src="/../images/unity/UniTask学习笔记/线程-1.png"></img>

Unity是单线程引擎，**Unity 的大部分 API 都是必须在主线程**（也称为 Unity 线程）上运行的，包括游戏对象的更新、UI 操作和物理引擎等。因此，无论是 `Coroutine`、`UniTask` 还是 `Task`，如果它们没有显式地切换到其他线程，**默认都会在主线程上运行**。



```c#
private async void Start()
{
    Debug.Log($"主线程ID: {Thread.CurrentThread.ManagedThreadId}");
    int result = await Task.Run(() =>
    {
        Debug.Log($"ExpensiveCalculation线程ID: {Thread.CurrentThread.ManagedThreadId}");
        return ExpensiveCalculation();
    });
}
```

<img class="half" src="/../images/unity/UniTask学习笔记/线程-2.png"></img>

**`Task.Run`是专门设计在后台线程上执行**任务，而不是主线程。主线程在执行 await 之后，会暂时释放控制权，等待任务完成，而任务则在后台线程上执行。



#### 将其他方法转换成UniTask方法

```C#
using (var cts = new CancellationTokenSource())
{
    await UniTask.WhenAll(
        ExampleUniTask(bar1, cts.Token),
        ExampleAsync(bar2, cts.Token).AsUniTask(),
        ExampleCoroutine(bar3).WithCancellation(cts.Token)
        );
}
```



#### 将UniTask转换成协程

```C#
IEnumerator ExampleCoroutine(HealthScrollbar healthScrollbar)
{
    yield return ExampleUniTask(_cts.Token).ToCoroutine();
}

async UniTask ExampleUniTask(CancellationToken token)
{
    for (int i = 0; i < 100; i++)
    {
        token.ThrowIfCancellationRequested();
        await UniTask.Delay(50);
        Debug.Log(i);
    }
}
```

