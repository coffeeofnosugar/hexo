---
title: 【Unity】DOTween
date: 2024-08-08 19:45:06
tags:
  - Unity
  - Unity动画
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



---

### Tweener

#### 控制播放周期

- **可以将其想象成视频的播放按钮，打开一个视频的时候他会开始自动播放，除非暂停。**

- **暂停之后，需要点击Play继续播放**

- **视频放完之后再次点击Play没用，只能Restart。**

`Tweener`方法如下

- `Play()`：继续播放动画，在实例化`Tweener`的时候就会
- `Pause()`：暂停动画，使用`Play()`继续播放
- `PlayForward()`：动画向前播放
- `PlayBackwards()`：动画向后播放
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



---

### 使用技巧

#### 改变数值

如果需要改变的是普通的数值，而不是Transform，可以使用一下方法

```c#
private DOGetter<float> _radiusGetter;	// 其实就是一个获取数值的委托
private DOSetter<float> _radiusSetter;	// 其实就是一个设置数值的委托

private void Awake()
{
    _radiusGetter = () => _light.pointLightOuterRadius;		// 定义委托
    _radiusSetter = newValue => _light.pointLightOuterRadius = newValue;	// 定义委托

    InputReader.Instance.AmplifyPressedEvent += AmplifyLight;	// 设置触发事件
}

private void AmplifyLight()
{
    DOTween.To(_radiusGetter, _radiusSetter, newValue, duration);// 执行DOTween动画——改变_radiusGetter获取的值
}
```

```C#
// 可以让 m_tmp999 的文字从 currentView 在1.2秒内平滑的变成 realCoin
// 从断点来看，第一个委托只有在第一次获取初始值时才会执行一次就不会再执行了；第二个委托每帧都会执行一次，value的值会慢慢接近 realCoin
var realCoin = LevelManager.Instance.LevelDataCollection.Coin;
var currentView = int.Parse(m_tmp999.text);
DOTween.To(() => currentView,
           value =>
           {
               m_tmp999.text = value.ToString();
           }, realCoin, 1.2f);
```











#### Sequence使用示例

```c#
private Sequence bounceSequence;

bounceSequence = DOTween.Sequence()
    // 添加一个向下移动的Tweener
    .Append(rect.DOAnchorPosY(rect.anchoredPosition.y - 150f, .1f).SetEase(Ease.OutQuad))
    // 添加一个还原的Tweener
    .Append(rect.DOAnchorPosY(rect.anchoredPosition.y, .2f).SetEase(Ease.OutQuad))
    .Pause()
    .SetAutoKill(false);

public void OnPointerClick(PointerEventData eventData)
{
    bounceSequence.Restart();	// 使用Restart()，表示这是一个可重复触发的动画
}
```



#### 倒放动画

```c#
private Tweener amplifyTween;

amplifyTween = rect.DOScale(1.2f, 0.2f).SetAutoKill(false).Pause();

public void OnPointerEnter(PointerEventData eventData)
{
    amplifyTween.PlayForward();		// 鼠标进入时，放大图片
}

public void OnPointerExit(PointerEventData eventData)
{
    amplifyTween.PlayBackwards();		// 鼠标离开时，倒放动画，即还原
}
```







#### 终止动画

当前dotween动画没播放完，便再次播放有冲突的操作，如连续多次播放、正播、倒播，导致显示不正常或报错。

解决方法：在每次开始执行播放动画时，先加上下面对应类似的杀死进程代码，就OK了

```c#
transform.DOKill();
transform.RectTransform().DOKill();
```



#### 忽略timeScale影响

让DOTweenAnimation忽略`Time.timeScale = 0`的影响

```C#
tween.SetUpdate(true);
```



#### 360度旋转

设置`Rotate`旋转模式

```C#\
transform.DOLocalRotate(new Vector3(0, 0, -360), 2, RotateMode.FastBeyond360)
                .SetEase(Ease.Linear).SetLoops(-1, LoopType.Restart).Play();
```



#### `Form()`

DOTween的参数默认都是目标值，使用From后参数代表起点

```C#
// 绝对位置，若当前坐标（1,0,0），即从5运动到1
transform.DOMoveX(5, 1).From();
transform.DOMoveX(5, 1).From(false);
 
// 相对位置，若当前坐标（1,0,0），即从6运动到1（6-1=5，相对位移5）
transform.DOMoveX(5, 1).From(true);
```



#### `SetLoops(int loops, LoopType loopType)`

- `loops`：循环次数，-1为无数次循环
- `loopType`：循环模式
  - `Restart`：从头开始循环（默认）
  - `Yoyo`：交替来回移动
  - `Incremental`：设置为相对运动后才生效，**连续**"向前"移动（A到B, B到B+(A-B), ...）



#### `SetRelative()`

设置为相对运动







#### `SetEase`

**这里可以参考 👉 [| https://easings.net | ](https://www.runoob.com/jqueryui/api-easings.html)👈 上的曲线效果**

<img class="half" src="/../images/unity/DOTween/SetEase.png"></img>

##### Flash

<img class="half" src="/../images/unity/DOTween/Flash.gif"></img>

##### 示例

<img class="half" src="/../images/unity/DOTween/SetEase-1.gif"></img>

<img class="half" src="/../images/unity/DOTween/SetEase-2.gif"></img>

<img class="half" src="/../images/unity/DOTween/SetEase-3.gif"></img>

<img class="half" src="/../images/unity/DOTween/SetEase-4.gif"></img>

<img class="half" src="/../images/unity/DOTween/SetEase-5.gif"></img>







---

### UniTask配合

想要将DoTween转换成UniTask，需要在ProjectSetting - Player - OtherSetting - ScriptingDefineSymbols中添加`UNITASK_DOTWEEN_SUPPORT`

优点：

- 可以使用await，而不是OnComplete回调函数，使代码更直观

  ```C#
  private async void Start()
  {
      await transform.DOMove(new Vector3(5f, 0, 5f), 2);			// 先移动
      await transform.DORotate(new Vector3(90f, 90, 90f), 2);		// 再旋转
      Debug.Log("Complete");										// 最后再输出
  }
  ```

- 可以使用WithCancellation方法取消DOTween

  ```C#
  public class UniTaskWithDOTween : MonoBehaviour
  {
      private CancellationTokenSource _cts = new CancellationTokenSource();
  
      private async void Start()
      {
          await transform.DOMove(new Vector3(5f, 0, 5f), 2).WithCancellation(_cts.Token);
          Debug.Log("Complete");
      }
  
      private void Update()
      {
          if (Mouse.current.leftButton.wasPressedThisFrame)
          {
              _cts.Cancel();
          }
      }
  
      private void OnDestroy()
      {
          _cts?.Dispose();
      }
  }
  ```

> 注意：
>
> - 如果想要重复使用tweenrs（`SetAutoKill(false)`），则永远不会触发await下方的代码
>
> - 如果想要等待另一个时间点，可以使用扩展方法`AwaitForComplete`, `AwaitForPause`, `AwaitForPlay`, `AwaitForRewind`, `AwaitForStepComplete`。
>
>   ```C#
>   public class UniTaskWithDOTween : MonoBehaviour
>   {
>       private Tweener tween;
>     
>       private void Awake()
>       {
>           tween = transform.DOMove(new Vector3(5f, 0, 5f), 2).Pause();
>       }
>     
>       private async void Start()
>       {
>           await tween.AwaitForPlay();		// 先是被挂起，当在Update中检测到鼠标右键点击后，再执行下方代码
>           Debug.Log("Play");
>       }
>     
>       private void Update()
>       {
>           if (Mouse.current.rightButton.wasPressedThisFrame)
>           {
>               tween.Play();
>           }
>       }
>   }
>   ```
>
>   







---

参考

[Unity Dotween插件的运动曲线（Ease）介绍Ease选项Ease效果示例以及C#修改动画曲线功能](https://blog.csdn.net/qq_33789001/article/details/124408540)
