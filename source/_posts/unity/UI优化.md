---
title: 【Unity】UI优化
date: 2024-11-07 20:05:06
tags:
  - Unity
  - UI
---

### 批处理

批处理的目的是为了减少Draw Call的调用次数



什么是Draw Call？

1. CPU先准备好模型的网格、用到的贴图和Shader，然后将网格、贴图、Shader加载到显存里面。
2. 然后是CPU设置渲染状态：每个网格用哪个Shader、贴图渲染。
3. CPU通知GPU开始渲染（通知的这个命令就叫做Draw Call）。



UGUI实质上也是由网格组成的，所以也会产生Draw Call



### 总结

#### 合批优化

- 使用图集
- 动静分离(动态部分和静态部分分别使用不同的Canvas)
- Text如果可以用图片代替就用图片代替
- 避免频繁删除/增加UI对象，UI层次结构变化会引起Canvas的更新(rebuild)
- 避免UI元素数目过多和层次结构过于复杂影响Batch更新速度
- 尽量不要使用Mask（其内部使用了模板缓冲，至少会造成增加2个Draw Call）

#### 其他优化

- 尽量不要使用Outline、TiledSprite（两者会产生许多顶点）
- 不需要点击事件的取消勾选Raycast







---

参考

[Unity3D UGUI系列之合批](https://blog.csdn.net/sinat_25415095/article/details/112388638)
