---
title: 【Unity】UI相关的一些判断
date: 2024-02-07 09:10:06
tags:
  - Unity
---

---

### `GraphicRaycaster`组件

<img class="half" src="/../images/unity/UI/GraphicRaycaster.png"></img>

Graphic Raycaster组件一般是和Canvas挂载在同一个物体下面
管理他下面的所有子UI物体的点击响应方式
在一些交互部件没响应的时候可以看下是不是这部分出问题了

如：

- 激活该组件时，用户从相机发射的摄像是会被挡住的
- 关闭该组件时，该Canvas下的UI组件如button，dropdown等都无法使用

注意Graphic Raycaster只对UI下的点击交互起作用，而Physics类里面的api不影响UI上面的交互

#### `Ignore Reversed Graphics`

这个属性是用来决定当交互部件水平或者垂直翻转到背面对着屏幕(不一定是180度，只要翻转到背面对着屏幕)的时候，是否忽略背面点击,勾上(翻转到背面不能点击) 取消勾选(不管怎么翻转都能点击)

#### `Blocked Objects`

这个属性决定了当有物体遮挡在UI前面，并且点击了遮挡部分的时候，是否应该忽略这次点击，
**Three D (3D)：**遮挡在本UI前的是带有3DCollider的物体,点击遮挡部分,忽略本UI的响应,(点自己没反应)
**Two D(2D):**遮挡在本UI前的是带有2DCollider的物体,点击遮挡部分,忽略本UI的响应,(点自己没反应)

**None:**不忽略本UI的点击，不管有3D/2D的物体挡住,都响应本UI的点击
**All:**都忽略响应,当UI前的遮挡物体是带有任意Collider组件的,点击遮挡部分的时候,都忽略本UI,(点自己没反应)

#### `Blocking Mask`

这个属性一般和Blocked Objects参数一起调节起作用，默认是EveryThing
遮挡的物体如果刚好在勾选的层级下面的话，会构成阻挡点击交互的作用

---

### `Canvas Group`组件

CanvasGroup可以影响该组UI元素的部分性质，而不需要费力的对该组UI下的每个元素进行逐一得得调整。Canvas Group是同时作用于该组件UI下的全部元素。

<img class="half" src="/../images/unity/UI/CanvasGroup.png"></img>

#### 参数

Alpha : 该组UI元素的透明度。注：每个UI最终的透明度是由此值和自身的alpha数值相乘得到。

Interactable : 是否需要交互（勾选的则是可交互），同时作用于该组全部UI元素。

Blcok Raycasts : 是否可以接收图形射线的检测（勾选则接受检测）。注：不适用于Physics.Raycast.。

Ignore Parent Group : 是否需要忽略父级对象中的CanvasGroup的设置。（勾选则忽略）

#### 应用场景

- 在窗口的GameObject上添加一个CanvasGroup，通过控制它的Alpha值来淡入淡出整个窗口

- 通过给父级GameObject上添加一个CanvasGroup并设置它的Interactable值为false来设置一套没有交互（灰色）的控制

- 通过将元素或元素的一个父级添加Canvas Group并设置BlockRaycasts值为false来制作一个或多个不阻止鼠标事件的UI元素

#### CanvasGroup的Alpha与SetActive()方法比较：

- CanvasGroup的Alpha与SetActive()两者之间的性能区别不大

- CanvasGroup的Alpha由0设为1的时候，并不会让自己活着的子节点中脚本执行Awake()方法，而SetActive(true)则会执行Awake()方法

- CanvasGroup的Alpha设为0和SetActive(false)的时候，同样不会调用drawcall

#### 小实例（一闪一暗）代码：

```C#
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
 
public class Test : MonoBehaviour {
 
    private float alpha0 = 0.0f;
 
    private float alphaSpeed = 2.0f;
    bool isShow;
 
    private CanvasGroup cg;
 
	void Start () {
        cg = this.transform.GetComponent<CanvasGroup>();
	}
	
	void Update ()
    {
        if (!isShow)
        {
            cg.alpha = Mathf.Lerp(cg.alpha, alpha0, alphaSpeed * Time.deltaTime);
            if (Mathf.Abs(alpha0 - cg.alpha) <= 0.01)
            {
                isShow = true;
                cg.alpha = alpha0;
                alpha0 = 1;
            }
        }
        else
        {
            //*0.5是因为从隐藏当显示感觉很快
            cg.alpha = Mathf.Lerp(cg.alpha, alpha0, alphaSpeed * Time.deltaTime * 0.5f);
            if (Mathf.Abs(alpha0 - cg.alpha) <= 0.01)
            {
                isShow = false;
                cg.alpha = alpha0;
                alpha0 = 0;
            }
        }
	}
 
}
```

---

### 判断鼠标是否在UI上

```C#
# true：在UI上，false：不在UI上
# 受GraphicRaycaster组件影响，鼠标在未激活GraphicRaycaster的canvas上时返回false
bool isOn = UnityEngine.EventSystems.EventSystem.current.IsPointerOverGameObject()
```



---

转载：
[unity Graphic Raycaster 作用详解](https://blog.csdn.net/Ling_SevoL_Y/article/details/107714884)
[Unity中CanvasGroup组件](https://blog.csdn.net/qq_38721111/article/details/89190006)
