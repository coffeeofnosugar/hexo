---
title: 【Unity】Animancer状态机源码学习笔记（一）
date: 2024-08-16 03:47:06
tags:
  - Unity
  - Unity动画
---

[官方](https://kybernetik.com.au/animancer/docs/manual/fsm/)的轻量免费版也提供了源代码，路径：`Assets/Plugins/Animancer/Utilities/FSM`

在本文中，标题将严格按照父类——子类的顺序排布

先列代码，后面是讲解。了减少文本量，不让文章看起来臃肿，有些代码不会贴



<img class="half" src="/../images/unity/Animancer学习笔记/State Machine.png"></img>

### 设计思路

#### 组件布局

`Character`组件是任何角色的核心，无论是玩家、敌人、NPC、人、动物、怪物还是机器人。
游戏中的所有角色应共享相同的标准脚本，该脚本包含对其每个其他组件的引用(通常很少有自己的逻辑)。

引用以下内容：

- 动画系统：`AnimancerComponent`或`Animator`
- 状态机：有限状态机、行为树
- 常见功能：`Rigidbody`，角色 属性、背包、生命值等

拥有这个中心脚本，意味着其他脚本可以简单地拥有对`Character`的一个引用，并通过它访问所有其他组件。

#### 动画播放方式

一句话来说就是，将组件当做一个状态，`OnEnable`的时候播放动画，在动画播放完的时候退出动画

`Animancer`的有限状态机采用在`MonoBehaviour`的`OnEnable`中播放动画，这样在控制组件的开启与关闭`enable`就可以控制这个动画的播放



---

### `StateMachine<TState>`

泛型类，需要传递`StateBehaviour`类，`partial`，在多个文件夹中存在

>  默认状态机
>
>  `StateMachine<TState>`中有一个默认的状态机`StateMachine<TState>.WithDefault`
>  如果没有自定义状态机的需求可以直接使用这个
>
>  特点：
>
>  - 不会跟踪除`CurrentState`以外的任何状态，`PreviousState`和`NextState`没有作用
>  - 被序列化之后可以引用`CurrentState`和`DefaultState`，如果`CurrentState`没有被设置值，那么状态机将立即进入`DefaultState`。<font color="DarkGray">所以也可以理解成，如果设置了`CurrentState`，那么状态机会立刻进入这个状态</font>
>  - 还具有`.ForceSetDefaultState(TState)`方法，通常用在动画结束时使用，时动画回到默认状态

这里先简单介绍一下默认状态机，`StateMachine<TState>`的详细源码将在下一章节展开



---

### `Character`

```C#
[DefaultExecutionOrder(-10000)]// Initialize the StateMachine before anything uses it.
public sealed class Character : MonoBehaviour
{
```

启动时机很早，不会再衍生类，能挂载到物体上

序列化：引用`AnimancerComponent`、状态机、血量、背包、武器等

```C#
private void Awake()
{
    StateMachine.InitializeAfterDeserialize();		// 反序列化之后，初始化状态机
}
```

该类主要是当做所有控制的中心脚本，起到牵线搭桥的作用，本身并没有多少逻辑，只有一个初始化方法





---

### `StateBehaviour`

```C#
public abstract class StateBehaviour : MonoBehaviour, IState
{
```

继承自`Monobehaviour`但本身是`abstract`类，所以无法被挂载到物体上

```C#
public virtual void OnEnterState()
{
    enabled = true;
}
public virtual void OnExitState()
{
    if (this == null)
        return;
    enabled = false;
}
```

该类主要的作用是在进入时启动脚本，在退出时关闭脚本：

{% note %}

除了关闭开启脚本外，该脚本还实现了接口的`CanEnterState`和`CanExitState`属性，默认永远都是`true`，后续有需求可自定义
{% endnote %}

```
#if UNITY_EDITOR
        protected virtual void OnValidate()
        {
            if (UnityEditor.EditorApplication.isPlayingOrWillChangePlaymode)
                return;

            enabled = false;
        }
#endif
```

挂载脚本的时候将脚本的设置为非启用。这么做是因为要将该组件设置成一个状态，这个状态是否启用就是通过`enable`管理并体现的的



#### `CharacterState`

```C#
public abstract class CharacterState : StateBehaviour
{
```

与父类一样，无法挂载到物体上

```C#
[System.Serializable]
public class StateMachine : StateMachine<CharacterState>.WithDefault { }
```

定义了一个状态机类，<font color="red">注意：这里只是定义，并没有实例化</font>，在[`Character`](#`Character`)中实例化了

> 那为什么不直接在`Character`中定义并实例化呢：
>
> 1. `StateMachine<>`的泛型参数是`Character`，写在这里方便观看
> 2. `Character`里需要定义一个名称为`StateMachine`的状态机，如果定义在`Character`中的话，就只能改一个名字了，如`CharacterStateMachine`
> 3. 这样处理能让`Character`的代码更加简洁
>
> 当然这些原因影响并不大，如果非得写在`Character`中也不是不行，取决于个人喜好

引用`Character`<font color="DarkGray">（就两行，不贴代码了）</font>

```C#
public virtual CharacterStatePriority Priority => CharacterStatePriority.Low;		// 设定动画的优先级
public virtual bool CanInterruptSelf => false;				// 设定动画是否可以被打断
```

```C#
public override bool CanExitState
{
    get
    {
        // There are several different ways of accessing the state change details:
        // var nextState = StateChange<CharacterState>.NextState;
        // var nextState = this.GetNextState();
        var nextState = _Character.StateMachine.NextState;
        if (nextState == this)					// 如果下一状态还是自己（即动画还没结束），就返回CanInterruptSelf
            return CanInterruptSelf;         
        else if (Priority == CharacterStatePriority.Low)
            return true;            			// 如果下个状态不是自己（即动画结束了），并且优先级是Low，就返回true
        else		 							// 如果下个状态不是自己（即动画结束了），并且就比较下一个状态的优先级
            return nextState.Priority > Priority;
    }
}
```

重写了`CanExitState`方法，重新设定状态的退出方法，

```
#if UNITY_EDITOR
        protected override void OnValidate()
        {
            base.OnValidate();

            gameObject.GetComponentInParentOrChildren(ref _Character);
        }
#endif
```

- 因为父类也写在`if UNITY_EDITOR`内，所以同样也得写在里面
- 挂载脚本的时候获取`Character`并赋值给`_Character`，这样就不用每次手动拖拽了



##### `IdleState`

```C#
[SerializeField] private ClipTransition _Animation;		// 引用动画
private void OnEnable()
{
    Character.Animancer.Play(_Animation);
}
```

在`OnEnable`的时候播放引用的动画。

<font color="red">注意：</font>

- 在游戏启动的时候`OnEnable`并不会触发，因为该组件的基类会将脚本设置为非启动，所以这里的`.Play()`并实际上并不会播放动画
- 将动画设置在`OnEnable`内还有另一个好处：当状态机启动该脚本时，就会播放动画



##### `ActionState`

引用`ClipTransition`动画

```C#
private void Awake()
{
    // 绑定事件，当动画播放结束时，将状态设置为默认状态。
    _Animation.Events.OnEnd = Character.StateMachine.ForceSetDefaultState;
}
private void OnEnable()
{
    Character.Animancer.Play(_Animation);	// 绑定事件，当动画播放结束时，将状态设置为默认状态。
}
```

```C#
// 重新设定优先级，使这个状态为Medium优先级，可被High打断，不可被Low打断。
public override CharacterStatePriority Priority => CharacterStatePriority.Medium;

// 重新设定，使这个状态可以被自身打断。
public override bool CanInterruptSelf => true;
```



---

### `BasicCharacterBrain`

用来监控玩家输入

```C#
[SerializeField] private Character _Character;		// 引用中心脚本
[SerializeField] private CharacterState _Move;		// 引用移动状态
[SerializeField] private CharacterState _Action;	// 引用攻击状态
```

```C#
private void Update()
{
    float forward = ExampleInput.WASD.y;					// 是否有按下W
    if (forward > 0)
        _Character.StateMachine.TrySetState(_Move);	// 按下了就TrySetState：当前状态不是目标状态，且目状态满足进入条件
    else
        _Character.StateMachine.TrySetDefaultState();	// 没按下就设置成默认状态
    if (ExampleInput.LeftMouseUp)
        _Character.StateMachine.TryResetState(_Action);		// 按下左键就转换到攻击状态
}
```

> `ExampleInput`是`Animancer.Examples`中的一个数据监测，从命名名称就可以看出作用，源代码也很简单，就不贴了









---

### `IState`接口

```C#
public interface IState
{
    bool CanEnterState { get; }
    bool CanExitState { get; }
    void OnEnterState();			// 在进入当前状态的时候会调用
    void OnExitState();				// 在退出当前状态的时候会调用
}
```

`bool CanEnterState`：当前状态是否能进入

- 由`StateMachine<TState>`的`.CanSetState`、`.TrySetState`和`.TryResetState`检查
- `StateMachine<TState>.ForceSetState`不判断，直接进入

`bool CanExitState`：当前状态是否能退出

- 判断条件同上

`Animancer`还提供了`DelegateState`类：

```
public class DelegateState : IState
{
    public Func<bool> canEnter;
    public virtual bool CanEnterState => canEnter == null || canEnter();
    public Func<bool> canExit;
    public virtual bool CanExitState => canExit == null || canExit();
    public Action onEnter;
    public virtual void OnEnterState() => onEnter?.Invoke();
    public Action onExit;
    public virtual void OnExitState() => onExit?.Invoke();
}
```

本身并没有实现任何功能，而是简单地为该接口的每个成员提供一个[委托](https://kybernetik.com.au/cs-unity/docs/introduction/methods/delegates)，以便在创建状态时分配它们。

### `CharacterStatePriority`枚举

```C#
public enum CharacterStatePriority		// 动画优先级
{
    Low,// Could specify "Low = 0," if we want to be explicit or change the order.
    Medium,// Medium = 1,
    High,// High = 2,
}
```







---

### 小结：

1. 第一次看源码，深刻体会到了一个优秀的架构能让程序更灵活，更有层次能让阅读者更容易理解，但是每个脚本太碎片化了，不容易维护。这个时候，接口的一个作用就体现了，能规定方法。并且充分使用`sealed`，`abstract`修饰符，能体现每个类的作用



2. 相比之前写的有限状态机有什么不同：

- 最让人眼前一亮的还是通过控制脚本组件的启用来完成进入和退出状态的操作，不仅使逻辑代码融入了`UnityBehaviour`生命周期，还能让开发者直观的看到每个状态的当前情况。<font color="DarkGray">有想过如果使用组件开关来实现状态机的进出，会不会影响性能问题。但是不管怎样，每个状态类都需要引用`Clip`你不得不序列化这个状态类</font>
- 之前并没有使用接口和父类继承，代码框架不够规范，做了很多重复的工作。每个状态之间太过独立，状态与状态之间的转换变得十分麻烦。如果想要扩展其他状态的话，几乎每个状态都得针对新的状态做出改变，可扩展性不强
- 引用了一个新的`Brain`脚本，用来控制每个状态之间的转换，而不是在状态内部控制跳到哪一个状态。每个状态内部只用管理自己是否能进入和退出，不用管什么时候进入。
- 有三种方式切换状态：`TrySetState`、`TryResetState`、`ForceSetState`，与`CanEnterState`和`CanExitState`配合能使动作之间的转变更加灵活。<font color="DarkGray">之前写的状态机只有类似`ForceSetState`这一种方式</font>



3. 关于`[System.Serializable]`：

​		之前只是简单的知道被这个属性修饰的类可以序列化展示在Inspector窗口上，现在了解到了一些其他的细节：

```C#
[System.Serializable]
public class Human
{
    public CharacterState a;
}

public class Test : MonoBehaviour
{
    public Human human;
}
```

通常我们实例化一个类需要使用` = new()`关键字。但是当这个类被`[System.Serializable]`修饰后，不需要使用`new`关键字，只要你在`MonoBehaviour`中声明了`Human human`，那么你就实例化它了<font color="DarkGray">（在Editor Mode的时候就已经被实例化了）</font>

