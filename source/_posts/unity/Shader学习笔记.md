---
title: 【Unity】Shader学习笔记
date: 2024-08-31 12:41:06
mathjax: true
tags:
  - Unity
  - Shader
---

### UV坐标

UV坐标是用于映射2D纹理到3D模型的坐标。在3D模型上的每个顶点都有一个对应的UV坐标，它告诉引擎在纹理上的哪个位置找到该顶点的颜色。

- UV坐标的范围通常是从(0,0)到(1,1)。左下角是原点(0,0)，右上角是(1,1)。

- 在三角形上，UV坐标会在三个顶点之间插值，以确保纹理正确地贴在整个三角形表面上。





---

### 数学运算符

运算本身并不难，难的是需要将运算与图形相结合。本单元在学习运算的同时学习一些其他的节点

#### `Add`

将两个`Texture`相加，通常是将一个颜色纹理与黑白图片相加：

- 白色`RGB`为1：同理，使颜色更亮

- 黑色`RGB`为0：任何数加0等于本身，所以**黑色部分显示内容不变**

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Add.png"></img>



#### `Multiply`、`Texture Coordinates`、`Time Parameters`、`Panner`

##### [`Texture Coordinates`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Texture_Coordinates)

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

##### [`Time Parameters`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Time_Parameters)

时间参数节点：输出Unity内部经过的时间(以秒为单位)



##### [`Panner`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Panner)

平移节点：根据`Time`按指定`Speed`移动UV坐标。若没指定速度，则使用默认速度

> NOTE：使用的Texture必须将`Wrap Mode`设置为`Repeat`



##### [`Multiply`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Multiply)

这里先只讨论单数值乘法

<img class="half" src="/../images/unity/Shader学习笔记/Multiply.gif"></img>

> NOTE：单数值乘法可交换位置，但是**矩阵乘法不可交换位置**





#### `Subtract`、[`World Position`](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/World_Position)

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



#### `Divide`、`Clamp`、`Lerp`、`Remap`

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Divide.png"></img>

##### `Divide`

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



##### `Clamp`

将输入的值，控制在范围内

如果与纹理坐标配合，就能控制显示的区域

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Clamp-1.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Clamp-2.png"></img>

{% endgrouppicture %}



##### `Lerp`

融合两个纹理

<img class="half" src="/../images/unity/Shader学习笔记/数学运算符-Lerp.gif"></img>



##### `Remap`

数据区间映射，将[Omin, Omax]上每个数映射到区间[Nmin, Nmax]上
$$ {\begin{equation} \label{eq1}
e=mc^2
$$ {\end{equation}

---



$$\begin{equation} \label{eq1}

e=mc^2

\end{equation}$$

