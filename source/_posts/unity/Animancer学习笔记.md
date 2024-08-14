---
title: 【Unity】Animancer学习笔记
date: 2024-08-15 3:47:06
tags:
  - Unity
---

### 基础概念

#### `AnimationClip`

Unity源生的一个类，引用指定的动画Clip。



#### `ClipTransition`

与`AnimationClip`类似，不仅能引用指定的Clip，还能使用内置方法管理如何播放这个`AnimationClip`



#### `AnimancerState`

`AnimancerComponent.Play()`返回的值——Clip控制器，可以用这个来控制Clip的属性：

- `.NormalizedTime`：归一化时间，该Clip的播放的进度
- `.Speed`：播放速度，负数可倒放



#### `AnimancerComponent.Play()`

动画控制器，三个参数，播放的动画引用`AnimationClip`或`ClipTransition`（后面将这两个统称为Clip）、过渡时间、播放方式



#### `NamedAnimancerComponent.TryPlay()`

- 可以使用使用名称字符串的形式播放动画，但是在这之前得先使用`NamedAnimancerComponent.State.Create(Clip)`创建一个状态

- 也可以直接使用引用`NamedAnimancerComponent.Play(Clip)`播放动画
- 将Clip直接放到`NamedAnimancerComponent.Animations`中时，并不会自动播放，除非勾选自动播放

总结一下：

可以使用`.TryPlay()`直接使用字符串名称播放指定动画，但是这个动画需要先存入`States`中



#### `ITransition`

`ITransition`是一个接口，通常unity不允许将接口序列化的展示到Inspector窗口上，但是`ITransition`已经使用[PropertyDrawer](https://docs.unity3d.com/ScriptReference/PropertyDrawer.html)做到能耐序列化接口了，只需在字段前面添加`[SerializeReference]`属性即可





---

### 动画速度与时间精度控制

### 倒放

直接向后播放：`Speed`设置为-1

从结尾向后播放：`NormalizedTime`设置为1



#### 暂停

- 调用`AnimancerComponent.Playable.PauseGraph()`停止动画，并不是时停，而是会将动画播放到结尾的位置

- 需要使用`.UnpauseGraph()`手动退出暂停状态
- <font color="red">非循环动画，在播放完一个动作后，AnimancerState.Time还在计算，照成不必要的性能消耗，应该使用`AnimancerComponent.Playable.PauseGraph()`来停止动画</font>，如果有必要的话还可以使用`AnimancerComponent.Evaluate()`将动画立即应用到对象上，例如在初始化的时候暂停动画。
- 从上面这点可以看出，如果暂停了动画并且后续没有动画变化，可以使用暂停，避免性能消耗



#### 时间

如果在动画最开始的时候调用了`AnimancerComponent.Playable.PauseGraph()`，动画处于暂停状态，并没有应用到人物上，这时就需要使用`AnimancerComponent.Evaluate()`，将当前的所有动画的状态应用到对象上了





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

当Inspector窗口的`AnimationClip _Open`被实例化了，并且`_Openness`的值被改变了，就会通过`MonoBehaviour Message`传递信息，实时反馈到场景中

![edit-mode](\images\unity\Animancer学习笔记\edit-mode.gif)

<img class="half" src="/../images/unity/Animancer学习笔记/edit-mode.gif"></img>
