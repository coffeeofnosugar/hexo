---
title: 【Unity】Spine学习笔记
date: 2024-10-05 16:54:06
tags:
  - Unity
---

[spine在Unity中的案例演示](https://www.bilibili.com/video/BV1te411g7ks/?spm_id_from=333.337.search-card.all.click&vd_source=56c4342823eb8458689563e7f2be4f99)

### 预览

<img class="half" src="/../images/unity/Spine学习笔记/Asset.png"></img>



### 设置混合

当需要

```C#
TrackEntry shootTrack = skeletonAnimation.AnimationState.SetAnimation(1, shoot, false);
shootTrack.AttachmentThreshold = 1f;	// 表示shoot在与其他动画融合时，依然会完整运行自己的动画
shootTrack.MixDuration = 0f;		// 表示进入shoot不需要融合
```

