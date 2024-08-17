---
title: 【Unity】Animancer状态机源码学习笔记（二）
date: 2024-08-16 09:40:06
tags:
  - Unity
  - Unity动画
---



<img class="half" src="/../images/unity/Animancer学习笔记/State Machine.png"></img>

 

本章将详细介绍[`StateMachine<TState>`](https://kybernetik.com.au/animancer/docs/manual/fsm/)，官方的轻量免费版也提供了源代码，路径：`Assets/Plugins/Animancer/Utilities/FSM`

该类由`partial`修饰，在四个文件中存在

- StateMachine1.cs
- StateMachine1.InputBuffer.cs
- StateMachine1.StateSelector.cs
- StateMachine1.WithDefault.cs

### StateMachine1.cs

```C#
[Serializable]
public partial class StateMachine<TState> : IStateMachine
    where TState : class, IState
{
```

实现接口、限制泛型类

```C#
[SerializeField]
private TState _CurrentState;
public TState CurrentState => _CurrentState;
```

序列化当前状态

```C#
public TState PreviousState => StateChange<TState>.PreviousState;
public TState NextState => StateChange<TState>.NextState;
```

引用静态访问点存储的上一个状态和正在进入的状态

```C#
public StateMachine() { }				// 因为是基类，这个方法只是起到一个占位的作用
public StateMachine(TState state)
{										// 创建一个新的结构体，三个参数分别是(状态机，上一个状态，下一个状态)
    using (new StateChange<TState>(this, null, state))	// 因为这个结构体是静态访问点，所以赋完值后可立即销毁
    {
        _CurrentState = state;			// 设置当前状态为下一个状态
        state.OnEnterState();			// 并立即进入这个状态，还记得OnEnterState是干嘛的吗——启动脚本enable = true
    }
}
```

构造函数，创建一个新的状态机，初始化`_CurrentState`的值，并立即进入这个状态

{% note info %}

因为后续会频繁的使用`using(new StateChange<TState>()){}`，这里解释一下：只有发起改变状态请求的时候才会使用到这个结构体，其他时候`StateChange<TState>()._Current`都是只有起到一个存储状态的作用

(without define class style)
{% endnote %}

```C#
public virtual void InitializeAfterDeserialize()
{
    if (_CurrentState != null)
        using (new StateChange<TState>(this, null, _CurrentState))
            _CurrentState.OnEnterState();
}
```

在序列化之后，尽快调用此方法，以正确的初始化`_CurrentState`。可以看到和上面的构造函数类似，因为序列化在Inspector上引用了`CurrentState`所以这里可以直接将其传递进来并初始化

> 拓展：
>
> `UnityEngine.ISerializationCallbackReceiver`接口无法实现自动初始化，这个接口的回调有很多unity的方法用不了，如`.OnEnterState()`里的`Behaviour.enabled`

```C#
public bool CanSetState(TState state)		// 判断当前状态机是否可进入指定状态
{
    using (new StateChange<TState>(this, _CurrentState, state))
    {
        if (_CurrentState != null && !_CurrentState.CanExitState)		// 如果当前状态不能退出，返回false
            return false;

        if (state != null && !state.CanEnterState)						// 如果目标状态不能进入，返回false
            return false;

        return true;
    }						// 在using结束的时候调用StateChange<TState>.Dispose()，确保线程静态成员_CUrrent状态正确
}
```

> 提一嘴：这里很容易将状态和状态机搞混。`CanSetState`是针对`状态机`的，而`.CanExitState`和`.CanEnterState`是针对状态的。
>
> 如果对`状态机`和`状态`的方法还有什么不清楚的，可以查看`IStateMachine`和`IState`接口

```C#
public TState CanSetState(IList<TState> states) { }	// 这个方法就是遍历并调用了上面的CanSetState方法，就不贴代码了
```

```C#
public void ForceSetState(TState state)			// 强制转换状态
{
    using (new StateChange<TState>(this, _CurrentState, state))
    {
        _CurrentState?.OnExitState();			// 立即执行当前状态的退出方法(disable组件)

        _CurrentState = state;					// 更新当前状态

        state?.OnEnterState();					// 立即执行新状态的进入方法(enable组件)
    }
}
```

```C#
public bool TrySetState(TState state) {}
public bool TrySetState(IList<TState> states) {}
public bool TryResetState(TState state) {}
public bool TryResetState(IList<TState> states) {}
```

这些方法都是在`CanSetState`和`ForceSetState`之上扩展，就不分析代码了。总的来说，一个判断，三种转换

```C#
public bool CanSetState(TState state) {}   // 判断当前状态是否能退出，目标状态是否能进入，并返回bool值结果

public bool TrySetState(TState state) {}   // 正常转换，目标状态不是当前状态，且目标状态满足进入条件，才转换
public bool TryResetState(TState state) {} // 尝试转换，目标状态能进入，就直接转换
public void ForceSetState(TState state) {} // 强制转换，无论当前状态、目标状态是否满足条件
```

> 最后是一个`Unity.Editor`在Inspector上显示的方法，暂时没看到效果，后续再补







---

### StateMachine1.InputBuffer.cs

这个文件夹中存放的是InputBuffers，即输入缓冲器。

作用：不是简单的改变状态失败就直接放弃了，而是还会尝试一小段时间。

类比：连续跳跃的时候，快要落地但实际上还没有落地的时候按下跳跃键，也能进入跳跃状态。

#### `InputBuffer<TStateMachine>`

包含在`StateMachine<TState>`类中的一个泛型类<font color="DarkGray">（并不是子类，只是包含关系，两个甚至可以说没有任何关系）</font>

缓存一个状态，每当`Update(float)`的时候尝试进入这个状态，直到`TimeOut`超时

```C#
public class InputBuffer<TStateMachine> where TStateMachine : StateMachine<TState>
{
```

限制传进来的类

```C#
private TStateMachine _StateMachine;		// 缓存目标状态机

public TStateMachine StateMachine
{
    get => _StateMachine;
    set
    {
        _StateMachine = value;				// 设置目标状态机，并清除之前的信息
        Clear();
    }
}
```

```C#
public TState State { get; set; }			// 需要进入的目标状态
public float TimeOut { get; set; }			// 倒计时，小于0就超时
public bool IsActive => State != null;		// 缓冲器状态，当目标状态为空时，就停止转换
```

```C#
public InputBuffer() { }				// 构造函数，占位用
public InputBuffer(TStateMachine stateMachine) => _StateMachine = stateMachine;		// 构造函数，指定状态机
```

```C#
public void Buffer(TState state, float timeOut)
{
    State = state;			// 设置目标状态和缓冲时间
    TimeOut = timeOut;
}
```

```C#
protected virtual bool TryEnterState() => StateMachine.TryResetState(State);	// 虚函数，可重构添加其他条件
public bool Update() => Update(Time.deltaTime);					// 在设置目标状态和缓冲时间之后再调用该方法
public bool Update(float deltaTime)						 // 尝试进入`state`状态，如果超时，就会调用Clear()方法
{
    if (IsActive)
    {
        if (TryEnterState())
        {
            Clear();
            return true;
        }
        else
        {
            TimeOut -= deltaTime;
            if (TimeOut < 0)
                Clear();
        }
    }
    return false;
}
```

```C#
public virtual void Clear()			// 清除任务
{
    State = null;
    TimeOut = default;
}
```

#### `InputBuffer`

```C#
public class InputBuffer : InputBuffer<StateMachine<TState>>
{
    public InputBuffer() { }
    public InputBuffer(StateMachine<TState> stateMachine) : base(stateMachine) { }
}
```

继承自`InputBuffer<TStateMachine>`，并确定了泛型参数为`StateMachine<TState>`，这个没好说的，就是指定了状态机

使用方法：

1. 需要在`update()`中调用输入缓冲器的`_InputBuffer.Update()`
2. 在需要改变状态的时候使用`_InputBuffer.Buffer(_Equip, _InputTimeOut)`











---

### StateMachine1.StateSelector.cs

这个文件夹中放置的是`StateSelector`， 即状态选择器

该类提供了一种简单的方法来管理潜在状态的优先级列表

#### `ReverseComparer<T>`

一个泛型类<font color="DarkGray">（并不是子类，只是包含关系，两个甚至可以说没有任何关系）</font>

```C#
public class ReverseComparer<T> : IComparer<T>
{
    public static readonly ReverseComparer<T> Instance = new ReverseComparer<T>();	// 饿汉单例
    private ReverseComparer() { }											// 私有构造函数，不需要用户创建实例
    public int Compare(T x, T y) => Comparer<T>.Default.Compare(y, x);		// 实现接口，定义比较方法，参数换位置了
}
```

这里需要注意的是

- 不需要用户实例这个类，所以将构造函数私有化了

- 比较的方法实用的是`Compare()`，在传参的时候，将两个参数的位置换了（第一个参数y小于x时返回-1）

  也就是说最终的效果是返回-1，y小x大；返回-1时，x小y大

#### `StateSelector`

包含在`StateMachine<TState>`类中的类

```C#
public class StateSelector : SortedList<float, TState>				// 继承`SortedList<float, TState>`类
{
    public StateSelector() : base(ReverseComparer<float>.Instance) { }		// 构造函数，并且将参数传递给父类的构造
    public void Add<TPrioritizable>(TPrioritizable state)		// 定义一个泛型方法
                where TPrioritizable : TState, IPrioritizable  // TPrioritizable必须满足TState和IPrioritizable
                => Add(state.Priority, state);		// 调用了基类的Add方法
}
```

- 继承`SortedList<float, TState>`类，所以拥有这个基类的所有属性，如`Add`

```C#
public virtual void Add(object key, object value);		// 基类SortedList的Add方法
```

实际上在使用的时候可以使用简单的枚举来配分动作的优先级，没必要用这种







---

### StateMachine1.WithDefault.cs

默认状态机，其实就是添加了一个默认状态，然后针对这个默认状态写了初始化和转换成默认状态方法

就是方便用户手册介绍产品使用的，如果自己使用的话完全可以重新写一个

```C#
[SerializeField]
private TState _DefaultState;			// 默认状态
public TState DefaultState
{
    get => _DefaultState;
    set
    {
        _DefaultState = value;
        if (_CurrentState == null && value != null)
            ForceSetState(value);
    }
}
```









---

### `StateChange<TState>`结构体

作用：查看状态变化细节的静态访问点

要看懂这个结构体，得先搞清楚以下几点：

1. 他的核心是`_Current`这个线程静态属性，所有其他属性都是围绕他而展开的
2. 这个结构体的用法：只有在`StateMachine`使用`IState`方法（即正在改变状态）的时候才需要创建这个结构体，结束后就会弃用掉这个临时的结构体（但由于`_Current`是静态的，所以`_Current`是还存在的）





```C#
public struct StateChange<TState> : IDisposable where TState : class, IState
{
```

限制类型参数，继承`IDisposable`接口

```C#
[ThreadStatic]
private static StateChange<TState> _Current;
```

当前状态变化，设置成了线程静态，所以每个线程都有自己的副本，使得整个系统是线程安全的

> 线程静态成员特点：
>
> 1. 多个线程访问并改变_Current的值时，每个线程看到的是它自己的 _Current 副本，因此一个线程对 _Current 的修改不会影响其他线程。
> 2. 每个线程在其生命周期内对 _Current 的任何修改只对其自身有效。当线程执行完毕后，该线程的 _Current 副本就会被销毁。
> 3. 当所有线程都执行完毕后，_Current 的最终值取决于最后一个修改它的线程的状态，或者如果没有任何线程正在进行状态更改，_Current 将保持其默认值（通常是 null 或者初始状态）。

```C#
private StateMachine<TState> _StateMachine;		// 当前发生状态变化的状态机实例
private TState _PreviousState;					// 正在被改变出去的状态
private TState _NextState;						// 正在进入的状态
```

```C#
public static bool IsActive => _Current._StateMachine != null;					// 是否正在发生变化
public static StateMachine<TState> StateMachine => _Current._StateMachine;		// 设置上面字段的访问器
public static TState PreviousState => _Current._PreviousState;
public static TState NextState => _Current._NextState;
```

{% note info %}

这里可以看到只提供了`PreviousState`和`NextState`两个状态供外界访问，外界没有访问`_Current`的方法，因为没有必要。

通过在`CanExitState`的打印这三个可以看出，`_Current`就是`PreviousState`。如`Idle`->`Jump`：

1. 在按下空格的一瞬间：`PreviousState`是`Idle`，`NextState`是`Jump`；

2. 起跳后系统每帧都在判断是否能从`Jump`->`Idle`，这段期间`PreviousState`一直是`Jump`，`NextState`一直是`Idle`；

3. 如果在空中的时候又按了一下空格键，系统会判断能否`Jump`->`Jump`，在你按下的这一帧`PreviousState`和`NextState`都是`Jump`

可以看出来这里的状态是相对于帧的状态，并不是指上一个状态块

<img class="half" src="/../images/unity/Animancer学习笔记/StateChange.png"></img>

<img class="half" src="/../images/unity/Animancer学习笔记/StateChange1.png"></img>

(without define class style)
{% endnote %}

```C#
internal StateChange(StateMachine<TState> stateMachine, TState previousState, TState nextState)
{
    this = _Current;

    _Current._StateMachine = stateMachine;
    _Current._PreviousState = previousState;
    _Current._NextState = nextState;
}
```

`internal`，只允许在`Animancer.FSM`内访问

构造函数用于设置当前状态变化的信息。它首先复制当前的`StateChange<TState>`到this，然后更新_Current以反映新的状态变化。

```C#
public void Dispose()
{
    _Current = this;
}
```

实现`IDisposable`接口，在`StateMachine<TState>`会常使用`using`来创建结构体，在`using`结束时将自己再存储在线程静态中。

<font color="DarkGray">其实整个的作用就是为了保证有且只有一个静态`_Current`并且其状态是最新的</font>

```C#
using (new StateChange<TState>(this, null, state))
{
    _CurrentState = state;
    state.OnEnterState();
}
```

> 拓展：`IDsposable`的作用：`using `块结束或其中的代码抛出异常 ，`Dispose` 方法将被自动调用











---

### `IStateMachine`接口

```C#
public interface IStateMachine
{
    object CurrentState { get; }		// 当前激活的状态
    object PreviousState { get; }		// 上一个状态
    object NextState { get; }			// 下一个状态
    bool CanSetState(object state);		// 当前是否可以进入指定的状态
    object CanSetState(IList states);	// 返回列表中第一个能进入的状态
    bool TrySetState(object state);		// 尝试设置某个状态，成功返回true。如果传进来的是当前状态，会立即返回true。想要再次播放当前状态可以使用`TryResetState(object)`
    bool TrySetState(IList states);		// 如果当前状态在实参中，则不做任何事直接返回true。想再次播放，方法同上
    bool TryResetState(object state);	// 尝试进入指定状态，此方法不会判断实参是否已经是当前状态
    bool TryResetState(IList states);	// 同上
    void ForceSetState(object state);
#if UNITY_ASSERTIONS						// 打包时不会编译if内的代码
    bool AllowNullStates { get; }		// 当前状态是否可为空
#endif
    void SetAllowNullStates(bool allow = true);
#if UNITY_EDITOR
    int GUILineCount { get; }
    void DoGUI();
    void DoGUI(ref Rect area);
#endif
}
```

`void ForceSetState(object state)`：强制改变状态

调用`CurrentState`的`IState.OnExitState`，然后将`CurrentState`改变成参数状态，并调用其`IState.OnEnterState`

### `IPrioritizable`接口

状态选择器使用的

```C#
public interface IPrioritizable : IState
{
    float Priority { get; }
}
```







---

### 总结：

​		第一次研究源码，开始的时候确实会被吓着，觉得有点困难什么的。但实际看完下来发现和之前学的状态机核心工作原理是差不多的，只是在这基础上完善了很多方法，如：设定进入、离开状态的方法；使用接口规范代码。看完之后发现其实理解的还是很通透的。

​		这次的奇妙之旅最大的搜获可能就是理解了一个完整的项目应该是怎么样的框架结构。要尽可能的使用接口和继承，达到解耦的效果，使代码更容易维护。

​		学习的路还很长，这次状态机的源码并不是`Animancer`的核心源码，只是其中的一个小部分而言，而且有限状态机也不是很难的一个模型。后续还需要继续研究源码，了解更多的编程技巧、模型框架。

