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

   <img class="half" src="/../images/unity/TEngine/热更新-1.png"></img>

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
   
7. (这步必不可少)运行菜单 HybridCLR/Build/BuildAssets And CopyTo AssemblyPath

8. 运行菜单TEngine/QuickBuild/一键打包AssetBundle

9. (可选)比较差异，运行菜单YooAsset/Extension/补丁包对比工具

   <img class="half" src="/../images/unity/TEngine/热更新-2.png"></img>

10. 替换热更新文件：(如果没有执行第九步，那么可以直接将所有文件上传，如果有重复的就替换该文件)，将第九步中显示的差异资产选择出来并

    <img class="half" src="/../images/unity/TEngine/热更新-3.png"></img>

    <img class="half" src="/../images/unity/TEngine/热更新-4.png"></img>

    > 经测试，可以将旧的bundle和信息等文件删除

11. 效果如下

    <img class="half" src="/../images/unity/TEngine/热更新-5.png"></img>







---

### 微信小游戏热更

1. 下载并安装[插件](https://game.weixin.qq.com/cgi-bin/gamewxagwasmsplitwap/getunityplugininfo?download=1)

2. 打包设置：

   - CDN地址需要填写在该面板下

     <img class="half" src="/../images/unity/TEngine/微信小游戏-1.png"></img>

   - 在Edit-ProjectSetting-TEngine-TEngineSettings的InnerResourceSource、ExtraResourceSource和FormalResourceSource中填写相同的地址

     <img class="half" src="/../images/unity/TEngine/微信小游戏-2.png"></img>

3. 点击生成并转换，生成微信小游戏

4. 部署资源

   - 老样子，先部署微信生成的资源，将./webgl/下的两个文件和一个文件夹上传服务器

     <img class="half" src="/../images/unity/TEngine/微信小游戏-3.png"></img>

     > 此步骤类似于设置游戏的StreamingAssets，只不过相对windows来说，咱们是吧StreamingAssets文件放置在了服务器上，而不是跟随着包体

   - 然后，创建文件夹./Default_0/WebGL/，将webgl里的文件再上传一次（）

     <img class="half" src="/../images/unity/TEngine/微信小游戏-4.png"></img>

     > 此步骤类似于设置游戏的远程热更新地址，启动游戏时会判断./addressable/Default_0/WebGL/PackageManifest_DefaultPackage.version与./addressable/StreamingAssets/package/DefaultPackage/PackageManifest_DefaultPackage.version，两个的版本号。从而来进行更新

5. 热更新，修改代码后

   - 运行菜单 HybridCLR/Build/BuildAssets And CopyTo AssemblyPath
   - 运行菜单TEngine/QuickBuild/一键打包AssetBundle
   - 将生成的补丁包放置在./addressable/Default_0/WebGL/下
