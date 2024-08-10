---
title: 【Unity】Odin
date: 2024-08-08 19:45:06
tags:
  - Unity
---

### 介绍

[DOTween官网教程](https://odininspector.com/tutorials)



---

### Inspector

比较简单，看示例就能懂

自定义`Editor`还挺好用的，后面有机会补



---

### Validator

总的来说大概有两种使用方法

1. 不使用语法糖，检测全局物体
2. 使用语法糖，检测指定的属性



有两种创建方式`RegisterValidator`、`RegisterValidatorRule`。这两个唯一不同的是，后者可以在Validator窗口上编辑是否禁用和配置其属性



#### Value Validator

**检测全局的**

比如说，相机必须要绑定角色，就可以通过这个方式来检测，具体代码如下

```C#
#if UNITY_EDITOR
using Sirenix.OdinInspector.Editor.Validation;

[assembly: RegisterValidator(typeof(CameraValidator))]

public class CameraValidator : ValueValidator<PlayerCamera>		// 我们需要检验所有的PlayerCamera脚本
{
    protected override void Validate(ValidationResult result)
    {
        if (Value.player == null)								// 判断PlayerCamera.player是否为空
            result.AddError("Camera need player");
    }
}
#endif
    
public class PlayerCamera : MonoBeahaviour
{
	public Transform player;
}
```

将这个脚本放在项目中就可以了，不用做其他操作。然后Validator就会找寻场景中所有使用了`PlayerCamera`脚本的实例，检查`player`是否为空

如果没有绑定角色，就会出现下图Error

<img class="half" src="/../images/unity/odin/相机检测.png"></img>





#### Root Object Validator

`Root Object Validator`非常适合验证Unity对象，例如ScriptableObject、Materials和Components。因为您只会收到对象本身的告警/错误消息，所以称为`Root`。

与`Value Validator`不同，在另一个对象中引用跟对象，不会引发额外的警告/错误



#### Attribute Validator

属于第一类，检测指定属性的







---

### Serializer

序列化用的，如果要实现存档，建议使用ES3
