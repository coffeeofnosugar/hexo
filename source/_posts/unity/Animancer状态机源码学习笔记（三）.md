---
title: 【Unity】Animancer状态机源码学习笔记（三）——StateChange
date: 2024-10-11 05:52:06
tags:
  - Unity
  - Unity动画
---

### 核心代码

```C#
public struct StateChange<TState> : IDisposable
    where TState : class, IState
{
    [ThreadStatic]  // 标记为线程静态
    public static StateChange<TState> _current;

    private StateMachine<TState> _stateMachine;
    private TState _previousState;
    private TState _nextState;

    internal StateChange(StateMachine<TState> stateMachine, TState previousState, TState nextState)
    {
        this = _current;    // 嵌套循环中上一层的 StateChange 暂存在 this 中，方便在 using 结束时复原

        _current._stateMachine = stateMachine;
        _current._previousState = previousState;
        _current._nextState = nextState;
    }

    public void Dispose()
    {
        _current = this;        // 在退出 using 时复原嵌套循环上一层的 StateChange
    }
}
```



#### 简介

- 使用：该结构体只有在转换状态的时候才会创建，并且在转换完成后销毁<font color="DarkGray">（但身为静态成员的_current依然存在）</font>

- 作用：

  1. **规范状态转换方法**：在调用`IState`的方法时，都需要在该结构体的作用域中。换言之，可以在`IState`的方法中访问上一个状态和下一个状态

  2. 主要作用：在执行**嵌套**循环时，能正确的返回上一层`StateChange`的数据



---

### 使用示例

下面将根据示例来展示`StateChange`的工作原理



#### 规范状态转换方法

在`StateMachine`中已经封装好了`StateChange`的创建，所以我们可以直接在`IState`的方法中访问`StateChange`的数据

```C#
public class AttackState : State
{
    StateMachine<State>.WithDefault _stateMachine;
    public AttackState(StateMachine<State>.WithDefault stateMachine)
    {
        _stateMachine = stateMachine;
    }

    public override void OnEnterState()
    {
        // 输出： 从 IdleState 进入 AttackState
        Debug.Log($"从 {_stateMachine.PreviousState} 进入 {_stateMachine.NextState}");
    }
}
```



#### 嵌套访问

假设当前从`FallState`->`RunState`，<font color="red">为方便测试，以下代码并不规范</font>

```c#
public class RunState : State
{
    // 在进入 RunState 时，可能需要判断是否应该返回 DefaultState 或者进入 HitState
    public override void OnEnterState()         // 第一层嵌套，FallState -> RunState
    {
        Debug.Log($"第一层嵌套开始 {_stateMachine.NextState}");    // 输出：第一层嵌套开始 RunState

        if (true)
        {
            _stateMachine.TrySetDefaultState();     // 第二层嵌套一号，RunState -> DefaultState
        }
        
		// 输出：第二层嵌套结束，继续第一次嵌套 RunState
        Debug.Log($"第二层嵌套结束，继续第一次嵌套 {_stateMachine.NextState}");    

         if (true)
        { 
            _stateMachine.TrySetState(_brain.hitState);     // 第二层嵌套二号，RunState -> HitState
        }
    }
}
```

上方的嵌套可以表示成

```C#
using (new StateChange<TState>(stateMachine, FallState, RunState))
{
    using (new StateChange<TState>(stateMachine, RunState, DefaultState))
    {
    }
    
    using (new StateChange<TState>(stateMachine, RunState, HitState))
    {
    }
}
```

状态的改变顺序

1. `FallState` -> `RunState`
2. `RunState` -> `DefaultState`
3. `DefaultState` -> `HitState`

- 最终的状态为`HitState`
- 其实这是一个错误示范，若`TrySetDefaultState`返回`true`，则应该`return`

> 如果在进入其他状态后没有return就会出现一个奇怪的问题：
>
> `第二层嵌套一号`已经退出`RunState`了，但是在继续执行第一层时，`_stateMachine.PreviousState`会变回成`RunState`
>
> <font color="red">注意</font>：
>
> - 在成功进入其他状态后需要return
> - 为了方便研究工作原理，我的所有状态继承的并不是`StateBehaviour`，而是最基础的`State`，如果查看`StateBehaviour`源码就能发现：真正进入状态才会执行的是`OnEnable()`方法，而不是`OnEnterState()`<font color="darkgray">（该方法可以看做是一个工具人，用来判断是否满足进入状态的条件，实际上并没有进入）</font>。
>   所以如果以上状态继承的是`StateBehaviour`，发生上面的改变顺序时，并不会执行`DefaultState.OnEnable()`。



---

### 嵌套访问实现原理

主要通过`using`作用域、 `StateChange()`构造函数和`Dispose()`实现

假设当前正在执行上面示例的第二层嵌套一号

```C#
public void ForceSetState(TState state)
{
    using (new StateChange<TState>(this, CurrentState, state))	// 将 FallState -> RunState 暂存在this中
    {
        CurrentState?.OnExitState();

        _currentState = state;

        state?.OnEnterState();
    }															// 将 FallState -> RunState 复原
}
```

```c#
internal StateChange(StateMachine<TState> stateMachine, TState previousState, TState nextState)
{
    this = _current;    // 将 FallState -> RunState 暂存在this中
 
    _current._stateMachine = stateMachine;		// 开始第二层嵌套一号
    _current._previousState = previousState;
    _current._nextState = nextState;
}
```

```c#
public void Dispose()
{
    _current = this;        // 将 FallState -> RunState 复原
}
```



---

### 总结

从这次的学习中，已经非常熟悉这套状态机的工作原理了，最需要注意的如下：

1. 如果继承的是`StateBehaviour`，规范的写法为
   - `OnEnterState()`用来**判断**能否进入状态
   - `OnEnable()`才是进入状态后真正需要执行的代码
2. 如果成功切换状态则需要`return`，避免再执行后续代码，导致又退出刚进入的状态
3. 虽然Animancer已经将`StateChange`封装好了，但我们还是得搞清楚它工作的作用：
   - 在`IState`的方法中，可以访问改变状态的参数
   - 在嵌套访问`IState`时，返回上一层嵌套可以复原状态



