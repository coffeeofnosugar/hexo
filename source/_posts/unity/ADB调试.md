---
title: 【Unity】ADB调试
date: 2026-01-06 11:29:06
tags:
  - Unity
---

手机打开开发者模式，并开启usb调试

在unity中打开如下窗口，在文件管理器中打开以下路径

<img class="half" src="/../images/unity/ADB调试/工具路径.png"></img>

打开路径下的platform-tools文件夹，在cmd中进入该路径

在cmd中输入`adb logcat -s Unity`随后即可在cmd中实时看到log日志，这样即使程序闪退也能看到日志了



如果觉得窗口不方便查看，或者中文是乱码，可以使用`adb logcat -s Unity -d > C:\Work\Project\UnityADBLog.txt`将日志输出到本地文件中





#### 引用

https://developer.aliyun.com/article/666214



#### 扩展

在打包安卓包体时，如果出现`UnityEngine.AndroidJavaException: java.lang.ClassNotFoundException`，如下

```C#
01-06 10:14:03.277 9615 9656 E Unity : [TapSDK] (Main) Failed to create instance of TapSDK.Core.Mobile.TapCoreMobile: System.Reflection.TargetInvocationException: Exception has been thrown by the target of an invocation. ---> System.TypeInitializationException: The type initializer for 'TapSDK.Core.BridgeAndroid' threw an exception. ---> UnityEngine.AndroidJavaException: java.lang.ClassNotFoundException: com.taptap.sdk.kit.internal.enginebridge.EngineBridge
01-06 10:14:03.277 9615 9656 E Unity : at UnityEngine.AndroidJNISafe.CheckException () [0x0008d] in /home/bokken/sharedspace/ra_2022.3/Modules/AndroidJNI/AndroidJNISafe.cs:24
01-06 10:14:03.277 9615 9656 E Unity : at UnityEngine.AndroidJNISafe.FindClass (System.String name) [0x0000c] in /home/bokken/sharedspace/ra_2022.3/Modules/AndroidJNI/AndroidJNISafe.cs:107
01-06 10:14:03.277 9615 9656 E Unity : at UnityEngine.AndroidJavaClass._AndroidJavaClass (System.String cl
```

可以在unity中右键Project窗口，使用以下两个方法清楚缓存并重新解析

- Assets - External Dependency Manager - Android Resolver - Delete Resolved Libraries
- Assets - External Dependency Manager - Android Resolver - Force Resolve

