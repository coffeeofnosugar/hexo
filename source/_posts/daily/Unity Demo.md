---
title: Unity Demo
date: 2024-08-05 14:51:31
tags: 日常
---


<link rel="stylesheet" href="/../css/base.css">
<link rel="stylesheet" href="/../css/center.css">
<link rel="stylesheet" href="/../css/images.css">



### 试玩网站

为了方便观看将[3DRPG](https://www.coffeeofnosugar.top/unitygame/3drpgv3/)游戏部署到了网站上https://www.coffeeofnosugar.top/unitygame/3drpgv3/


由于头发的物理模拟并不支持WebGL，所以头发看起来像塑料一样

### 介绍视频

### 行为树 & 第三人称控制器

{% raw %}
<div style="position: relative; width: 100%; height: 0; padding-bottom: 75%;">
<iframe src="//player.bilibili.com/player.html?isOutside=true&aid=112907996171197&bvid=BV1nxaoeNELZ&cid=500001638921677&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" style="position: absolute; width: 100%; height: 100%; Left: 0; top: 0;"></iframe>
</div>
{% endraw %}

### 行为树编辑器

使用UI Builder**从零制作**怪物行为树可视化编辑器，通过视图连接各个节点，实现定制化怪物AI。

- 使用面向对象的方式规范节点代码，使代码清晰易维护
- 使用UI Builder实现**自定义节点外观**，可更改各个节点显示文本内容、颜色和形状等
- 使用UI Builder实现引擎窗口视图自定义化，展示自定义Inspector与Blackboard窗口，并**实时更新展示的数据**
- 使用C#代码定制**逻辑控制器节点**
  - Repeat节点：重复执行子节点
  - Selector节点：依次执行子节点，直到所有子节点执行完毕或有一个子节点返回Success，Selector节点停止运行并且也返回Success
  - Sequencer节点：依次执行子节点，直到所有节点执行完毕或有一个子节点返回Failure，Sequencer节点停止运行并且也返回Failure
  - Weight节点：给每个子节点设置一个权重，按照权重选择一个子节点执行，并返回与该子节点一样的结构
- 使用C#代码定制行为树**动作节点**
  - Wait节点：设置延迟时间，执行到该节点时在此停留设置的时间
  - TargetDistance节点：设置距离，判断与Target的距离，小于设置的距离返回Failure，大于设置的距离返回Success，通常与Selector节点一起使用
  - MoveToTarget节点：开启Run动画，设置移动速度，朝向Target移动，并根据agent的路径状态停止移动，以防卡住
  - RandomPosition节点：随机获取起始点附近的一个点位，通常与MoveToPosition节点一起使用
  - MoveToPosition节点：移动到RandomPosition节点随机获取到的点位上
  - Log节点：打印设置的message信息
  - Skill节点：通过在怪物节点中设置的技能cd和技能释放距离判断是否达到释放技能条件，达到释放条件后将释放此技能
- 通过行为树窗口视图连接逻辑控制器节点和动作节点，实现定制化怪物AI
- 在PlayerMode下可以通过行为树视图实时观察怪物当前状态


<div class="container">
    <img src="/../images/daily/项目/行为树1.png"></img>
    <img src="/../images/daily/项目/行为树2.png"></img>
</div>



---

### 第三人称控制

- `CharacterController`控制玩家移动
- 有限状态机模式控制玩家状态
- `Input System`监听玩家输入
- `Animator`控制玩家动画，下一步计划将舍弃`Animator`转而使用`Playable`播放动画





