---
title: 【Unity】Animancer状态机源码学习笔记（四）——使用示例
date: 2024-10-14 08:48:06
tags:
  - Unity
  - Unity动画
---

### 创建状态类

#### 状态基类选择

共有两个类使用了`IState`接口，另外其中一个类还衍生出了一个专门供角色使用的子类

- `State`：非常纯粹的使用`IState`，无其他任何操作。适用于一些简单的FSM。
- `StateBehaviour`：除了使用`Istate`外，还继承了`MonoBehaviour`。适合需要在Inspector上序列化的FSM。
  - `CharacterState`：继承自`StateBehaviour`，因为角色的状态大多数都无法打断自己（无法从Idle再次进入Idle），该类针对这个问题做了特殊处理

如果需要创建角色FSM的话，毫无疑问的就需要继承`CharacterState`了

#### 代码示例

状态类里的逻辑越简单越好，只需要做状态类的逻辑判断，<font color="red">不要做状态转换</font>

##### 使用方法

```C#
public class MoveState : CharacterState
{
    private void OnEnable()
    {
        Debug.Log("播放Move动画");
    }
}
```

##### 最好不要做切换逻辑

状态类只用处理自己状态内的逻辑，不要做转换逻辑（转换逻辑应该在Brain中判断）。除非是特殊的事件状态（如攻击、死亡）结束后可以使用`TrySetDefaultState`返回默认状态。

```C#
public class IdleState : CharacterState
{
    private void OnEnable()
    {
        Debug.Log("播放Idle动画");
    }

    private void Update()
    {
        // 不要出现如下状态转换的逻辑，这种逻辑应该在PlayerBrain里做
        // if (Input.GetKeyDown(KeyCode.Space))
        // {
        //     _stateMachine.TrySetState(State.Air);
        // }
    }
}
```

##### 特殊事件

优先级与强制转换使用场景

```C#
public class AttackState : CharacterState
{
    [SerializeField]
    private PlayerBrain1 _brain;
    private int _animationTime = 1000;
    private void OnEnable()
    {
        Debug.Log("播放Attack动画");
        AnimationDelay();
    }

    // 将攻击状态设置为中优先级，避免被其他状态打断
    public override CharacterStatePriority Priority
        => CharacterStatePriority.Medium;

    private async void AnimationDelay()
    {
        await Task.Delay(_animationTime);               // 模拟动画播放
        _brain.StateMachine.ForceSetDefaultState();     // 在动画播放完毕后强制设置成默认状态
    }
}
```





### 创建Brain类

用来控制Player在应该进入什么状态

#### StateMachine基类选择

有两个可供选择，分别对应着后缀为1和2的文件

- `StateMachine1`：在进入状态时需传入状态类这个对象实例。
- `StateMachine2`：在进入状态时只用输入对应的枚举。对序列化友好，但是需要额外的精力去维护。

对于Player状态机这两个都可以



#### StateMachine1示例

注意事项：<font color='red'>在Update中转换时，必须要使用if等逻辑判断处理好进入状态的顺序，不要出现成功进入A状态后继续转换，导致进入了B状态。</font>

错误示范：

```C#
private void Update()
{
    if (在空中)
        FSM.TrySetState(State.Air);         // 角色在空中，成功进入了空中状态
    FSM.TrySetState(State.Idle);            // 但是还会继续执行Update，导致进入Idle状态。
    // 最终表现在游戏中的结果是玩家疯狂在这两个状态中切换
}
```

正确示范：

```C#
private void Update()
{
    if (在空中)
        FSM.TrySetState(State.Air);         // 角色在空中，成功进入了空中状态
    else
        FSM.TrySetState(State.Idle);        // 角色不在空中，则进入Idle状态
}
```



源码：

```C#
public sealed class PlayerBrain1 : MonoBehaviour
{
    public StateMachine<CharacterState>.WithDefault StateMachine = new();

    [SerializeField] private CharacterState _idleState;
    [SerializeField] private CharacterState _moveState;
    [SerializeField] private CharacterState _attackState;


    private void Start()
    {
        // 初始化状态机，需要选择默认状态，在使用ForceSetDefaultState等方法时会进入该状态
        StateMachine.InitializeAfterDeserialize(_idleState);
    }

    private void Update()
    {
        UpdateMovement();
        UpdateAttackAction();
    }

    private void UpdateMovement()
    {
        if (Input.GetAxis("Horizontal") != 0)
        {
            // 两种方法进入状态
            StateMachine.TrySetState(_moveState);
            // _stateMachine.TrySetState(_moveState);
        }
        else
        {
            StateMachine.TrySetState(_idleState);
        }
    }

    private void UpdateAttackAction()
    {
        if (!Input.GetMouseButtonDown(0)) return;
        StateMachine.TrySetState(_attackState);
    }
}
```





#### StateMachine2示例

状态机的使用方法上面已经说的很清楚了，这里就只说一下使用枚举与类实例的区别

```C#
public sealed class PlayerBrain2 : MonoBehaviour
{
    private enum State { Idle, Move }

    [SerializeField]
    private StateMachine<State, CharacterState>.WithDefault _stateMachine = new();

    [SerializeField] private CharacterState _idleState;
    [SerializeField] private CharacterState _moveState;

    private void Awake()
    {
        // 需要映射枚举与状态的关系
        _stateMachine.AddRange(
            new [] { State.Idle , State.Move },
            new [] { _idleState, _moveState});
    }

    private void Start()
    {
        // 可以使用枚举初始化
        _stateMachine.InitializeAfterDeserialize(State.Idle);
    }

    private void Update()
    {
        UpdateMovement();
    }

    private void UpdateMovement()
    {
        if (Input.GetAxis("Horizontal") > .1f)
            _stateMachine.TrySetState(State.Move);      // 可以使用枚举做状态转换，而不需要类的实例
        else
            _stateMachine.TrySetState(State.Idle);
    }
}
```



