---
title: 【Unity】Animancer学习笔记
date: 2024-08-15 3:47:06
tags:
  - Unity
  - Unity动画
---

### 使用注意点

1. 在初始化阶段暂停了动画，可以使用`AnimancerComponent.Evaluate()`，将动画立即应用到物体上，否则可能会出现人物还是T-Post状态
2. 非循环动画在播放完动作后，且后续没有其他动画时，AnimancerState.Time依然在计算，为了避免不必要的性能开销，应该使用`AnimancerPlayable.UnpauseGraph`暂停动画
3. 当物体被OnDisable的时候，应该将使用`AnimancerPlayable.UnpauseGraph`取消动画的暂停。如果不取消，系统将会再次初始化一遍。`if (_Animancer != null && _Animancer.IsPlayableInitialized) _Ainmancer.Playable.UnpauseGraph();`
4. 在初始化的时候可以使用`AnimancerComponent.GetOrCreate(ITransition)`来检查`AnimancerState`是否存在







### 基础内容

#### Clip动画片段

- `AnimationClip`：Unity源生的一个类，引用指定的动画Clip。

- `ClipTransition`：与`AnimationClip`类似，不仅能引用指定的Clip，还能使用内置方法管理如何播放这个`AnimationClip`

- `ITransition`：是一个接口，通常unity不允许将接口序列化的展示到Inspector窗口上，但是`ITransition`已经使用[PropertyDrawer](https://docs.unity3d.com/ScriptReference/PropertyDrawer.html)做到能耐序列化接口了，只需在字段前面添加`[SerializeReference]`属性即可

<img class="half" src="/../images/unity/Animancer学习笔记/Clip介绍.png"></img>



#### `AnimancerState`

`AnimancerComponent.Play()`返回的值——Clip控制器，可以用这个来控制Clip的属性：

- `.NormalizedTime`：归一化时间，该Clip的播放的进度
- `.Speed`：播放速度，负数可倒放



### 组件

这里的组件都是Animancer帮我们做的好组件，是代替`Unity.Animator`的`Controller`的。所以在引用这些组件之后，就不需要配置`Controller`了

#### `AnimancerComponent.Play()`

动画控制器，三个参数，播放的动画引用`AnimationClip`或`ClipTransition`（后面将这两个统称为Clip）、过渡时间、播放方式

<img class="half" src="/../images/unity/Animancer学习笔记/AnimancerComponent.png"></img>



#### `NamedAnimancerComponent.TryPlay()`

- 可以使用使用名称字符串的形式播放动画，但是在这之前得先使用`NamedAnimancerComponent.State.Create(Clip)`创建一个状态

- 也可以直接使用引用`NamedAnimancerComponent.Play(Clip)`播放动画
- 将Clip直接放到`NamedAnimancerComponent.Animations`中时，并不会自动播放，除非勾选自动播放

总结一下：

可以使用`.TryPlay()`直接使用字符串名称播放指定动画，但是这个动画需要先存入`States`中

<img class="half" src="/../images/unity/Animancer学习笔记/NamedAnimancerComponent.png"></img>

#### 

#### `SoloAnimation`

性能不一定最好，同样的事，传统的`Animation`同样能做到，并且性能稍微好一点点。

他的用途仅限于需要使用人形或Generic Rig，并且只想播放一个动画的情况

<img class="half" src="/../images/unity/Animancer学习笔记/SoloAnimation.png"></img>





---

### 动画速度与时间精度控制

### 倒放

直接向后播放：`Speed`设置为-1

从结尾向后播放：`NormalizedTime`设置为1



#### 暂停

- 调用`AnimancerComponent.Playable.PauseGraph()`停止动画，并不是时停，而是会将动画播放到结尾的位置

- 需要使用`.UnpauseGraph()`手动退出暂停状态
- <font color="red">非循环动画在播放完动作后，AnimancerState.Time依然在计算，照成不必要的性能消耗，应该使用`AnimancerComponent.Playable.PauseGraph()`停止动画</font>，如果有必要的话还可以使用`AnimancerComponent.Evaluate()`将动画立即应用到对象上，例如在初始化的时候暂停动画。
- 从上面这点可以看出，如果暂停了动画并且后续没有动画变化，可以使用暂停，避免性能消耗



#### 时间

如果在动画最开始的时候调用了`AnimancerComponent.Playable.PauseGraph()`，动画处于暂停状态，并没有应用到人物上，这时就需要使用`AnimancerComponent.Evaluate()`，将当前的所有动画的状态应用到对象上了



#### 抽帧

`AnimancerComponent.Evaluate(value)`：将时间提前value秒，并立即应用所有的当前状态

```C#
private void Update()
{
    var time = Time.time;
    var timeSinceLastUpdate = time - _LastUpdateTime;
    if (timeSinceLastUpdate > 1 / _UpdatesPerSecond)
    {
        _Animancer.Evaluate(timeSinceLastUpdate);
        _LastUpdateTime = time;
    }
}
```

> 拓展：
>
> 1. 使用另外一个脚本，通过距离判断是否执行这个Update方法或这个Component，就可以降低原理玩家的怪物的动画。值得注意的是，Unity调用`MonoBehaviour`事件方法（如OnEnable或Update）都比在C#中正常调用方法开销更大。所以如果能使用一个单例脚本来管理怪物的动画抽帧，更能提高性能，但是这个方法也更复杂。可以不用每帧都判断，可以每隔10帧判断一下。`Renderer.isVisible`也是不错的方法
> 2. 使用这种方法可能会影响`Animation Evnets`和`Animancer Events`





---

### Root Motion

#### 添加Apply Root Motion属性

<font color="DarkGray">开启Root Motion，并不一定是很好的选择，很多游戏并没有开启Root Motion功能</font>

Animancer并没有给我们添加默认的是否运用Root Motion选项，需要我们自己绑定一个变量：

创建一个实现`ITransition`或继承[Transition Type](https://kybernetik.com.au/animancer/docs/manual/transitions/types/)的类，就可以将额外的数据绑定到动画上

```C#
[Serializable]
public class MotionTransition : ClipTransition
{
    [SerializeField, Tooltip("Should Root Motion be enabled when this animation plays?")]
    private bool _ApplyRootMotion;
    public override void Apply(AnimancerState state)
    {
        base.Apply(state);
        state.Root.Component.Animator.applyRootMotion = _ApplyRootMotion;
    }
}
```

<img class="half" src="/../images/unity/Animancer学习笔记/继承ClipTransition.png"></img>

- 使用`OnAnimatorMove`方法，将Root Motion动画的移动效果让人为可控
- 使用Root Motion后人物的移动与物理相关，如果人物使用的是`Rigidbody`控制移动的话，应该将`Animator`的`UpdateMode`设置为`AnimatePhysics`。这样他就只会被物理更新移动，也就是在FixedUpdate更新而不是Update中

#### Root Motion重定向

通常我们会将角色的逻辑`Component`与模型分开，如下

<img class="half" src="/../images/unity/Animancer学习笔记/hierarchy.png"></img>

这时就需要使用重定向，将`Animator`的动作映射到父节点上。不然父节点会留在原地，只有模型会前进

`Animancer`已经为我们封装好了，使用`RedirectRootMotionToCharacterController`、`RedirectRootMotionToRigidbody`、`RedirectRootMotionToTransform`脚本，将其放置在模型上并设置相应的`Animator`和`Target`属性就好了。源码很简单





---

### [线性混合](https://kybernetik.com.au/animancer/docs/examples/locomotion/linear-blending/)

通常需要根据人物的移动速度播放`idle`、`walk`或`run`，Unity源生的解决办法是`Blend Tree`（`Animancer`也可以使用并控制动画），`Animancer`提供了叫做`Mixer State`（类似于`Blen Tree`）的方法

#### 使用`Blend Tree`

##### 引用`Bled Tree`：

<font color="DarkGray">`ControllerTransition`类似`ClipTransition`可以引用`Unity.RuntimeAnimatorController`，这里面可以配置`Blend Tree`</font>

##### 参数控制

引用到`Unity.Blend Tree`之后，就可以参数来控制动画的播放状态了。`Animacer`也为我们准备了一个控制器来做这件事。

`Float1ControllerTransition`一个`ScriptableObject`类。可以引用指定的`Unity.RuntimeAnimatorController`，还能控制里面`Blend Tree`的单浮点混合树的参数

##### 使用方法

创建一个脚本引用`AnimancerComponent`组件和`Float1ControllerTransition`使用`_animancer.Play(Comtroller)`就可以播放里面的`Blend Tree`了。然后改变`Blend Tree`的参数，就可以改变动画状态了

```C#
public sealed class LinearBlendTreeLocomotion : MonoBehaviour
{
    [SerializeField] private AnimancerComponent _Animancer;
    [SerializeField] private Float1ControllerTransitionAsset.UnShared _Controller;

    private void OnEnable()
    {
        _Animancer.Play(_Controller);
    }
    /// <summary>Controlled by a <see cref="UnityEngine.UI.Slider"/>.</summary>
    public float Speed
    {
        get => _Controller.State.Parameter;
        set => _Controller.State.Parameter = value;
    }
}
```



#### [使用`Mixer State`](https://kybernetik.com.au/animancer/docs/samples/mixers/linear/#mixer)

官方原文：

[Mixer States](https://kybernetik.com.au/animancer/docs/manual/blending/mixers) are essentially just [Blend Trees](https://docs.unity3d.com/Manual/class-BlendTree.html) which are constructed using code at runtime instead of being configured in the Unity Editor as part of an Animator Controller. Specifically, they *can* be constructed using code and you *can* access their internal details even though in this example we are just using a [Transition](https://kybernetik.com.au/animancer/docs/manual/transitions).

>  翻译：
>
> [混合器状态](https://kybernetik.com.au/animancer/docs/manual/blending/mixers)本质上只是[混合树](https://docs.unity3d.com/Manual/class-BlendTree.html)，它们是在运行时使用代码构建的，而不是在 Unity 编辑器中配置为动画控制器的一部分。具体来说，它们*可以*使用代码构建，并且您*可以*访问它们的内部详细信息，即使在本示例中我们仅使用[Transition](https://kybernetik.com.au/animancer/docs/manual/transitions) 。

> 旧版本：
>
> 与使用`Bled Tree`的方法类似，也需要用到参数控制器。只需将上面代码的`Float1ControllerTransitionAsset.UnShared`替换成`LinearMixerTransitionAsset.UnShared`就可以了

v8.0版本：<font color="DarkGray">学着学着官方来了波大的，直接更新了一个大版本</font>

使用`Assets/Create/Animancer/Transition Asset`创建一个[`Transition Assets`](https://kybernetik.com.au/animancer/docs/manual/transitions/assets/)将其改成`LinearMixerTransition`类型，然后添加动画、设置动画参数就可以使用了<font color="DarkGray">v8.0引入了一个新的功能，`String Asset`</font>

`Assets/Create/Animancer/String Asset`创建一个`String Asset`

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/Animancer学习笔记/movement-speed-parameter.png"></img>

<img class="half" src="/../images/unity/Animancer学习笔记/mixer-transition.png"></img>

{% endgrouppicture %}













---

### Editor

想要使用某个值，将他应用到动画设置里，但是又嫌进入PlayMode麻烦，可以使用写一个`void OnValidate()`方法：

```C#
[SerializeField] private AnimationClip _Open;
[SerializeField, Range(0, 1)] private float _Openness;

#if UNITY_EDITOR
        private void OnValidate()
        {
            if (_Open != null)
                AnimancerUtilities.EditModeSampleAnimation(_Open, this, _Openness * _Open.length);
        }
#endif
```

当Inspector窗口的`_Open`被实例化并且`_Openness`的值被改变了，就会通过`MonoBehaviour Message`传递信息，实时反馈到场景中

<img class="half" src="/../images/unity/Animancer学习笔记/edit-mode.gif"></img>





---

### 属性

#### [数据单位](https://kybernetik.com.au/animancer/docs/manual/other/units/)

- `Meters`：在Inspector窗口中显示一个`m`，表达这个数据的单位是米
- `DegreesPerSecond`：`°/s`，旋转角度，度每秒
- `MetersPerSecond`：`m/s`，移动速度，米每秒
- `Multiplier`：`x`，倍率
