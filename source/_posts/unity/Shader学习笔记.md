---
title: 【Unity】Shader学习笔记
date: 2024-08-31 12:41:06
mathjax: true
tags:
  - Unity
  - Shader
---

### 自己总结的小规律

#### 数据类型

在Shader中，共有4种数据类型：

- 数学数据类型：`float`、`int`、`bool`;向量：`Vector2`、`Vector3`、`Vector4`;矩阵：`float2×2`、`float3×3`、`float4×4`
- UV坐标
- Texture纹理：人物(物体)蒙皮、法线、Mask遮罩<font color="DarkGray">（黑白分明有规则的图案）</font>、Noise噪声<font color="DarkGray">（黑白混乱的图案）</font>
- 像素点的世界坐标

尤其需要注意UV坐标和纹理这两类：

数学数据类型、世界坐标自不用说，在学习的过程中经常容易把UV坐标、蒙皮、Mask遮罩搞混。
尤其是UV坐标，UV坐标在`ShaderGraph`中是以图片展示其每个像素的数值，但其实UV坐标与Texture完全不一样。

- UV坐标是用于映射2D纹理到3D模型的坐标，举例来说：**UV坐标是中介，类似地图，2D纹理需要根据UV坐标找到在3D模型上自己应该对号入座的位置**
- 物体蒙皮：草地、金属棒球棒、墙面等纹理与形状关系不大的纹理可以随意复用；但是人体蒙皮的纹理与形状强关联，就不能随意复用
- 法线：一般也是人体这种与形状关联性强的纹理需要使用，用来**计算光照**
- Mask遮罩：黑白分明且有规则的图案，**通常用来裁剪其他纹理**，因为是黑白分明的图案，所以在计算的时候能发酵出很奇妙的结果
- Noise噪声：黑白混乱的图案，**通常与其他纹理组合**，无规则的黑白图案能实现随机的效果

每个作用不一样，在计算的时候要各司其职，不要混淆

> 总之
>
> - UV坐标是一个正经的二维正方形，初始状态左下角为(0, 0)，右上角为(1, 1)。其主要作用是告诉纹理该如何对号入座到3D模型上
> - 纹理存储着纹理数据，每个像素点上存储着`RGBA`值
>
> 用类来区分UV坐标和纹理：
>
> ```C#
> class UV
> {
>     int u;
>     int v;
> }
> 
> class Texture
> {
>     int u;
>     int v;
>     Vector4 color;		// `RGBA`颜色数据
> }
> ```







---

### UV坐标

UV坐标是用于映射2D纹理到3D模型的坐标。在3D模型上的每个顶点都有一个对应的UV坐标，它告诉引擎在纹理上的哪个位置找到该顶点的颜色。

- UV坐标的范围通常是从(0,0)到(1,1)。左下角是原点(0,0)，右上角是(1,1)。

- 在三角形上，UV坐标会在三个顶点之间插值，以确保纹理正确地贴在整个三角形表面上。









---

### [节点](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Nodes)

运算本身并不难，难的是需要将运算与图形相结合，并且不要把关键性的几个概念搞混

#### --------------数学运算符-------------

#### [`Add`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Add)(相加)：叠加两个纹理

将两个`Texture`相加，通常是将一个纹理与遮罩(Mask)相加：

- 白色`RGB`为1：同理，使颜色更亮

- 黑色`RGB`为0：任何数加0等于本身，所以**黑色部分显示内容不变**

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Add.png"></img>



#### [`Multiply`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Multiply)(乘法)

- 数值乘法：如下图

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Multiply-1.gif"></img>

- 纹理乘法：通常是纹理和遮罩相乘，以裁剪图片

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Multiply-2.gif"></img>

> NOTE：单数值乘法可交换位置，但是**矩阵乘法不可交换位置**



#### [`Subtract`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Subtract)(减法)

> 更改`Surface`为`Transparent`可以设置透明度百分比，而不是单纯的显示/透明
>
> <img class="half" src="/../images/unity/Shader学习笔记/透明度.png"></img>
>
> 这里只是一个扩展，继续我们的学习，将`Surface`改回`Opaque`

设置透明通道阈值`Alpha Clip Threshold = 0`，意味着当`Alpha`小于阈值使就会隐藏

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/Shader学习笔记/透明阈值1.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记/透明阈值2.png"></img>

{% endgrouppicture %}



如下图所示，物体的每个像素都会计算一遍这个减法，如果该像素的Y坐标减去1.75小于0，就会变透明

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Subtract.png"></img>



#### [`Divide`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Divide)(除法)：设置锐利度

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Divide-1.png"></img>

红框①的内容：

1. 原本U输出的内容是：从左到右逐渐远离0到达1
2. 与`Float1 = 0.5f`相减：
   - 左边：`0 - 0.5 = 0.5`，依然是黑色
   - 中间：`0.5 - 0.5 = 0`，变为黑色
   - 右边：`1 - 0.5 = 0.5`，变为灰色

绿框②的内容：

3. 与`Float2 = 0`相除：
   - 左边：`0 / 0 = 0`，依然是黑色
   - 中间：`0 / 0 = 0`，依然是黑色
   - 中间偏右：`0.00001 / 0 = 1`，变为白色
   - 右边：`0.5 / 0.5 = 1`，变为白色

可以看出**除法一般是用来设置锐利度的**

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Divide-2.gif"></img>



#### [`Clamp`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Clamp)(限制)：控制显示的区域

将输入的值，控制在范围内

如果与纹理坐标配合，就能控制显示的区域

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Clamp-1.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Clamp-2.png"></img>

{% endgrouppicture %}

> Tips：
>
> 需要与Scale节点区分开
>
> - Scale：裁剪掉其他区域
> - Clamp：其他区域依然显示，只是显示的不是原来的纹理，而是单色



#### [`Remap`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Remap)(映射)：归一化

数据区间映射，将[Omin, Omax]上每个数映射到区间[Nmin, Nmax]上
$$
N_{xy} = \frac{N_{max} - N_{min}}{O_{max} - O_{min}} \times (O_{xy} - O_{min}) + N_{min}
$$

上述公式的[Latex](https://so.csdn.net/so/search?q=Latex&spm=1001.2101.3001.7020)表达式：

```markdown
N_{xy} = \frac{N_{max} - N_{min}}{O_{max} - O_{min}} \times (O_{xy} - O_{min}) + N_{min}
```

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Remap-1.png"></img>

为方便理解，这里我们使用浮点数代替二维数，运作方式和结果是一样的
$$
\begin{split}
output &= \frac{1 - 0}{2 - 1} \times (1.5 - 1) + 0 \\
&= 1 \times 0.5 \\
&= 0.5
\end{split}
$$
最后输出的结果是0.5，与右边的颜色一样。

其实这里可以看出来，这里的数据很友好。`Float1`的值正好将[1, 2]映射到[0, 1]上了

- 1     对应  0
- 1.5  对应  0.5
- 2     对应  1

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Remap-2.gif"></img>



#### [`Lerp`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Lerp)(线性插值)：融合两个纹理

融合两个纹理

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Lerp.gif"></img>



#### [`One Minus`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/One_Minus)(1-)：1-input

out = 1 - input，对与UV坐标和遮罩很有用，可以将Texture纹理变为负片

- UV坐标：翻转两次，右上角翻转到左下角，左上角翻转到右下角

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-OneMinus-1.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-OneMinus-2.png"></img>

{% endgrouppicture %}

- 遮罩Mash：黑白颜色翻转

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-OneMinus-3.png"></img>

- 纹理：变为负片

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-OneMinus-4.png"></img>



#### [`Negate`](http://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Negate)(相反)：相反数

将输入的值变为相反数

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Negate.gif"></img>

> Tips：
>
> - 世界坐标输出的Global Preview为球形
>
> - UV坐标和纹理是方形



#### [`Scale`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Scale)(缩放)：裁剪区域

这个节点的Global Preview显示有问题，改变缩放数值后需要重新连接输入接口才能正常显示

- UV坐标：改变纹理缩放大小<font color="DarkGray">（与`Tilling`作用一样，再与`offset`可以选择展示的位置）</font>

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Scale-1.gif"></img>

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Scale-2.png"></img>

{% endgrouppicture %}

- 纹理：改变颜色的亮度

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Scale-3.gif"></img>

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Scale-4.png"></img>

{% endgrouppicture %}



#### [`Saturate`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Saturate)(饱和)：归一化

- input < 0           => output = 0
- 0 < input < 1     => output = input
- input > 1           => output = 1

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Saturate-1.png"></img>

常于`Lerp`节点配合

从下图可以看出，在使用`Saturate`节点之后，Y坐标大于1的值也是按1来计算的

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Saturate-2.gif"></img>



#### [`Sign`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Sign)(符号)：硬化

- input < 0           => output = -1
- input = 0           => output = 0
- input > 1           => output = 1

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Sign-1.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Sign-2.gif"></img>



#### [`Abs`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Abs)(绝对值)

- input < 0           => output = -input
- input = 0           => output = 0
- input > 1           => output = input

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Abs-1.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Abs-2.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Abs-3.gif"></img>

> Tips：
>
> `Relay`节点没有任何操作，只是为了Debug出图形



#### --------------UV坐标-------------

#### [`Texture Coordinates`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Texture_Coordinates)(UV坐标)

纹理坐标：定义纹理如何映射到3D资源上

- `Tiling`：纹理填充
- `Offset`：偏移参数

从下图可看出，设置`Tiling`为(2,2)之后，图片纹理在水平和垂直方向上各增加了一个纹理<font color="Darkgray">（前提是需要将`Wrap Mode`设置为`Repeat`）</font>

<img class="half" src="/../images/unity/Shader学习笔记/TextureCoordinates.png"></img>

{% tabs Unique name %}

<!-- tab 输出UV -->

输出完整的纹理坐标

- 左下角为(0, 0)，为黑色
- 左上角为(0, 1)，为绿色
- 右下角为(1, 0)，为红色
- 右上角为(1, 1)，为黄色

这里的颜色只是为了方便表述描绘二维数值的大小，没有什么特殊的含义，不要被颜色给迷惑了<font color="DarkGray">（顺带一提颜色正好对应着`RGBA`中的`(R, G)`）</font>

<img class="half" src="/../images/unity/Shader学习笔记/TextureCoordinates_UV.png"></img>

<!-- endtab -->



<!-- tab 输出U -->

输出纹理的横坐标

- 左边为0，右边为1
- 从左到右逐渐远离0，到达1

<img class="half" src="/../images/unity/Shader学习笔记/TextureCoordinates_U.png"></img>

<!-- endtab -->



<!-- tab 输出V -->

输出纹理的纵坐标

- 下边为0，上边为1
- 从下到上逐渐远离0，到达1

<img class="half" src="/../images/unity/Shader学习笔记/TextureCoordinates_V.png"></img>

<!-- endtab -->

{% endtabs %}



#### [`Panner`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Panner)(平移)：平移UV坐标

平移节点：根据`Time`按指定`Speed`移动UV坐标。若没指定速度，则使用默认速度

> NOTE：使用的Texture必须将`Wrap Mode`设置为`Repeat`



#### --------------Time-------------

#### [`Time Parameters`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Time_Parameters)(时间)

时间参数节点：输出Unity内部经过的时间(以秒为单位)







