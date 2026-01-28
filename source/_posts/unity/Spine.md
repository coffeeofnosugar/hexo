---
title: 【Unity】Spine
date: 2026-01-28 16:25:06
tags:
  - Unity
  - Spine
---

### 设置动画到指定帧

```C#
    public void SetAnimation(string _animationName, int _frame)
    {
        var skeletonData = skeleton.skeleton.Data;

        var state = skeleton.AnimationState;
        Spine.Animation animationToUse = !string.IsNullOrEmpty(_animationName) ? skeletonData.FindAnimation(_animationName) : null;
        if (animationToUse != null)
        {
            var trackEntry = state.GetCurrent(0);
            if (trackEntry == null || trackEntry.Animation.Name != _animationName || trackEntry.IsComplete && !trackEntry.Loop)
                trackEntry = state.SetAnimation(0, animationToUse, false);
            else
                trackEntry.Loop = false;

            // if (_playing)
            //     trackEntry.TimeScale = 1;
            // else
            {
                trackEntry.TimeScale = 0;
                trackEntry.TrackTime = Mathf.Lerp(0, trackEntry.AnimationEnd - trackEntry.AnimationStart, _frame / 100f);
            }
        }
        else
            state.ClearTrack(0);
    }
```

