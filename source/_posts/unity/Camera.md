---
title: 【Unity】Camera
date: 2026-02-12 15:49:06
tags:
  - Unity
---

### 如何设置正交相机的Size

默认 Unity 的 Orthographic 相机会根据 Size 设置**竖直方向的世界高度**，而宽度则是自动根据屏幕宽高比来扩展的，所以在不同的分辨率下看到的横向内容其实是不一样的

美术给过来的规格一般是720*1280，并且应该将相机的Size设置为6.4

根据正交相机的横向世界宽度计算公式为：

```C#
worldWidth = 2 * orthoraphicSize * (Screen.width / Screen.height)
```

此时worldWidth = 7.2，也就是说，**在该分辨率下横向能看到 7.2 单位世界宽度**



有了这个公式和worldWidth后，就可以反推其他分辨率下应该如何设置Size

如果我们希望所有分辨率下都能看到7.2单位世界宽度，那么应该使用以下公式

```#
orthographicSize = worldWidth * 0.5 / (Screen.width / Screen.height)
```

