---
title: 【Unity】TEngine
date: 2025-02-25 15:06:06
tags:
  - Unity
  - 框架
  - 热更新
---

---

### 热更新

学习测试，本打包流程以`OfflinePlayMode(单机模式)`做示范：

拉取[项目工程](https://github.com/Alex-Rachel/TEngine)后

1. 运行菜单 HybridCLR/Install... 安装HybridCLR，每次更新HybridCLR版本需要重新执行一次安装。

2. 运行菜单 HybridCLR/Define Symbols/Enable HybridCLR 运行开启HybridCLR热更新。

3. 运行菜单 HybridCLR/Generate/All 进行必要的生成操作。这一步不可遗漏!!!

4. 运行菜单 HybridCLR/Build/BuildAssets And CopyTo AssemblyPath，生成热更新dll并copy到热更程序集中。

5. 运行菜单TEngine/QuickBuild/一键打包window，

   <img class="half" src="/../images/unity/TEngin/热更新-1.png"></img>

6. 更改任意代码

   ```C#
   using TEngine;
   
   namespace GameLogic
   {
       [Window(UILayer.UI)]
       public partial class UITest : UIWindow
       {
           protected override void OnCreate()
           {
               // m_textTitle.text = "UI测试";
               m_textTitle.text = "热更新";
           }
       }
   }
   
   ```

7. 运行菜单 HybridCLR/Build/BuildAssets And CopyTo AssemblyPath

8. 运行菜单TEngine/QuickBuild/一键打包AssetBundle

9. (可选)比较差异，运行菜单YooAsset/Extension/补丁包对比工具

   <img class="half" src="/../images/unity/TEngin/热更新-2.png"></img>

10. 替换热更新文件：(如果没有执行第九步，那么可以直接将所有文件上传，如果有重复的就替换该文件)，将第九步中显示的差异资产选择出来并

    <img class="half" src="/../images/unity/TEngin/热更新-3.png"></img>

    <img class="half" src="/../images/unity/TEngin/热更新-4.png"></img>

    > 经测试，可以将旧的bundle和信息等文件删除

11. 效果如下

    <img class="half" src="/../images/unity/TEngin/热更新-5.png"></img>
