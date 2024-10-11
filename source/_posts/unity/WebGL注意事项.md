---
title: 【Unity】WebGL注意事项
date: 2024-10-11 18:37:06
tags:
  - Unity
---

---

### <font color="red">多线程</font>

`WebGL`环境不支持多线程，因此：

- 不能使用：`System.Threading`或`Task.Run()`之类的多线程操作
- 不能使用：Burst编译的`JobSystem`也是多线程

> `多线程编程`和`异步编程`是两个不同的概念
>
> WebGL支持异步编程
>
> - 可以使用：`async`和`Task`（只要没有使用`Tak.Run()`将任务调到新的线程上就OK）
> - 可以使用：`IEnumerator`协程
> - 可以使用：`UniTask`是完全在PlayerLoop上运行的，没有使用Thread（除了`UniTask.Run`和`UniTask.SwitchToThreadPool`）



### <font color="red">文件系统访问限制</font>

WebGL是运行在浏览器中的，没有访问本地系统的权限：

- 不能使用：`System.IO`访问本地文件

> - 可以使用：`Resources`, `StreamingAssets`, `PersistentDataPath`
> - 可以使用：`WWW`或`UnityWebRequest`加载远程资源



### <font color="red">数值精度</font>

- JavaScript 只有一种数值类型 `Number`（64位双精度浮点数），用来表示所有的数值，包括整数和浮点数

- Unity的`float`（32位单精度浮点数），即便在WebGL上运行，`float`的精度还是会维持在32位导致精度损失，不如直接使用64位的`double`
- GPU在某些情况下会降级浮点数的精度，当`float`降级成16位时，对该数据的影响就非常大了

> 拓展：
>
> - 精度降级不一定只发生在WebGL上，会发生在所有GPU计算上，尤其是涉及图形渲染
> - 通常分为16/32/64三个等级精度
> - 16位浮点数：
>   - 规则：
>     - 1位符号位，表示正数或负数
>     - 5位指数位，表示数值的范围
>     - 10位尾数位，表示数值的精度
>   - 范围：
>     - 最小正数：`0.000061`
>     - 最大正数：`65504`
> - 32位范围：`1.175×10^−38`~`3.4×10^38`
> - 64尾范围：`2.225×10^−308`~`1.8×10^308`





### 缺失功能和插件

- <font color="red">部分插件无法使用</font>，如`Magica Cloth 2`，插件是否支持WebGL具体查看插件官方文档
- 不支持本地系统API，如访问操作系统功能、摄像头等
  - `System.DateTime`函数可能会表现的不同
  - `System.Reflection`执行效率较低
  - 不支持的API在打包时能看到警告



### 音频限制

- 格式：WebGL支持的音频格式有限，建议使用 `.ogg` 或 `.mp3` 格式

- 延迟:由于浏览器的音频API限制，播放音频时可能有延迟，特别是首次播放音频。



### 调试

- 可以使用<kbd>F12</kbd>查看`Debug.Log`日志，但无法调试





---

### 内存管理

浏览器分配的内存有限

- 优化代码：
  - 避免过多的动态分配内存，防止内存泄漏
  - 手动释放不需要的资源（如`Texture`, `Mesh`, `List`等）
- 资产：使用更小的纹理、网格和其他资源



### 性能优化

- 减少Draw Calls
- 限制帧率，以减少CPU负担





