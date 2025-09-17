---
title: 【Unity】FGUI踩坑

date: 2025-09-17 22:29:06
tags:
  - Unity

---

## TMP+Fgui坑

#### 表现

首次打开UI时出现一帧GPU耗时超高的帧，紧接着下一帧是一帧CPU耗时超高的帧，里面具体的是Gfx，就是在等待GPU渲染完成。具体到编辑器上就是整个游戏直接卡住一会，再出现UI，到手机上更加明显。

#### 原因

<img src="/..\images\unity\FGUI踩坑\原因1.png" alt="img" style="zoom: 80%;" />

<img src="/..\images\unity\FGUI踩坑\原因2.png" alt="img" style="zoom: 80%;" />

这一帧GPU里有好几次TMP图集的复制操作，一次复制一个2048*2048的图集，重复十几次，导致GPU飙得很高，然后就都是同一张一模一样的图集复制好几份，不知道是要干嘛

#### 解决

把TMP的FontAsset的设置改为1024*1024的，就直接好了，这时候TMP图集会自动分页，就好了？不知道是个什么原理





## 点击事件坑

部分手机型号在使用fgui时可能会丢失点击事件

[原贴1](https://ask.fairygui.com/?/question/27373)

[原贴2](https://ask.fairygui.com/?/question/27465)

解决方案：使用使用unity原生的Input System

[官方文档](https://www.fairygui.com/docs/unity/input)：直接增加`FAIRYGUI_INPUT_SYSTEM`的宏即可





## UI加载坑

在使用AddPackage之后，需要使用LoadAllAssets将所有的资源都加载一遍，否则在第一次打开ui时依然会卡顿一下

```C#
private void AddPackageAsync(byte[] data, string key)
{
    UIPackage.LoadResourceAsync LoadPackageInternalAsync = async (string name, string extension, System.Type type, PackageItem item) =>
    {
        name = name.Replace("_fui", "");
        //异步加载包关联对象
        var a = await ResourceManager.instance.LoadAsset<UnityEngine.Object>(name);
        //设置资源
        item.owner.SetItemAsset(item, a, DestroyMethod.Unload);
    };
    var _package = UIPackage.AddPackage(data, key, LoadPackageInternalAsync);
    _package?.LoadAllAssets();
}
```

