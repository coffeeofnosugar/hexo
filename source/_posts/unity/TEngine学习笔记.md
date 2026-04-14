---
title: 【Unity】TEngine学习笔记
date: 2026-04-14 15:39:06
tags:
  - Unity
  - TEngine

---

# 加载资源方法

## 加载SO文件

### 一般加载资源用法：

```C#
// 获取句柄
var h = GameModule.Resource.LoadAssetSyncHandle<SkillConfigHelper>(nameof(SkillConfigHelper));
// 加载句柄
await h.ToUniTask();
// 执行逻辑
_instance = h.AssetObject as SkillConfigHelper;
// 释放句柄
h.Release();
// 最好再调用一下卸载无用资源
GameModule.Resource.UnloadUnusedAssets();
```

如果未执行Release，会存在两个`SkillConfigHelper`。

<img class="half" src="/../images/unity/TEngine学习笔记/未执行Release.png"></img>

执行Release，但不执行UnloadUnusedAssets，其中一个引用数量会变成0

<img class="half" src="/../images/unity/TEngine学习笔记/未执行UnloadUnusedAssets"></img>

执行Release，并且执行UnloadUnusedAssets

<img class="half" src="/../images/unity/TEngine学习笔记/执行Release和UnloadUnusedAssets"></img>



#### 框架内部加载资源方法

```C#
var h = await GameModule.Resource.LoadAssetAsync<BuffConfigHelper>(nameof(BuffConfigHelper));
```

如果不需要使用了，可以使用`GameModule.Resource.UnloadAsset(h)`释放掉，当然前提是没有任何其他对象对该SO有任何引用了。

<img class="half" src="/../images/unity/TEngine学习笔记/框架内部加载资源方法"></img>



## 加载GameObject

### 加载预制体

```C#
var root1 = await GameModule.Resource.LoadAssetAsync<GameObject>($"background_{levelConfig.MapImage}");
```

没错，就是与加载SO一样

> 注意：
>
> 1. 如果再次加载，框架内部已经处理好了，不会让你多次引用句柄
>
> 2. 如果不再使用了，需要释放掉，不然会一直存在内存中。
>
>    ```C#
>    GameModule.Resource.UnloadAsset(root1);
>    GameModule.Resource.UnloadUnusedAssets();
>    ```

### 直接生成实例

会实例化资源到场景，无需主动UnloadAsset，Destroy时自动UnloadAsset。

> 除了这两个，其他都必须在不再使用后释放掉。


```C#
// 同步
GameModule.Resource.LoadGameObject(assetPath);
// 异步
await GameModule.Resource.LoadGameObjectAsync(assetPath);
```
