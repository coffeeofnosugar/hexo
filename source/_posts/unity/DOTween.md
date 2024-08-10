---
title: 【Unity】DOTween
date: 2024-08-08 19:45:06
tags:
  - Unity
---

### 介绍

[DOTween官网](http://dotween.demigiant.com/documentation.php)

- `Tweener`和`Sequence`是`Tween`的子类
- `Tweener`是播放的单个动画
- `Sequence`控制`Tweener`的播放



#### 容易踩坑点

- 一个`Tweener`的循环为3时，那么他们三个算一个完整的动画

- 当`Tweener`添加到`Sequence`之后`Tweener`的大部分属性设置会被覆盖，比如循环，`Pause()`

- **最容易照成的误区**，动画为从原点向前移动5，`Restart()`之后将**重复刚才的动画**，也就是说他**会先回到原点**再向前移动5

- 如果为设置`SetAutoKill(false)`会在动画播放完一次之后就销毁掉，并且使用`_sequence.Restart()`并不会有反应，如果动画不是第一次播放，并且没有效果的话，可以检查一下定义这个动画的时候有没有使用`SetAutoKill(false)`。但是在使用`SetAutoKill(false)`之后，记得在合适的时候使用`_sequence = null`销毁掉对象，避免内存泄漏



### Tweener

#### 控制播放周期

- **可以将其想象成视频的播放按钮，打开一个视频的时候他会开始自动播放，除非暂停。**

- **暂停之后，需要点击Play继续播放**

- **视频放完之后再次点击Play没用，只能Restart。**

`Tweener`方法如下

- `Play()`：继续播放动画，在实例化`Tweener`的时候就会
- `Pause()`：暂停动画，使用`Play()`继续播放
- `Restart(bool, float)`：重新开始播放动画；是否忽略Sequence
- `Kill(bool)`：结束动画；如果为true就**瞬间**完成动画，false停在当前位置



#### 回调函数

动画周期内触发的回调：

- `OnStart`：只有在**第一次播放**时才会回调
- `OnPlay`：在**动画开始播放**时回调：第一次播放、`Play()`、暂停后的`Play()`、`Restart()`
- `OnUpdate`：动画播放的期间回调，**最好不要嵌套再嵌套**
- `OnStepComplete`：在每次完成一个循环时都会触发，**以为着，如果loops为3将被调用3次，而`OnComplete`只在最后被回调一次**
- `OnComplete`：在整个动画完成时调用，包括循环
- `OnPause`：在**动画停止播放**时回调，播放完整个动画、`Pause()`、`Kill(true)`

需用户手动触发的回调：

- `OnKill`：触发`kill()`时回调
- `OnRewind`：触发`Restart()`时回调
- `OnWayPoineChange`：唯一一个有参数的回调，主要用于`DoPath`函数，当走到一个点位时回调
