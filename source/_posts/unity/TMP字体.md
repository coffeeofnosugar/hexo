---
title: 【Unity】TMP字体
date: 2025-09-17 17:02:06
tags:
  - Unity

---

## 创建字体

<img class="half" src="/../images/unity/TMP字体/创建字体.png"></img>

Characters.txt内容如下，其中里面可以有重复的文字，TMP在生成的时候也自会生成一份

```Te
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 `~!@#$%^&*()_+-×÷=,./;'[]\<>?:"{}|·　！￥…（）—，。、；‘’【】《》？：“”〔〕丨丶丿乛□‰≤≥℃ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９｀～＠＃＄％＾＆＊＿＋－＝．／＇［］＼＜＞＂｛｝
获得角色
坚持时间
造成伤害
历史最高
返回
重新挑战
斗失败
攻击
速
暴击
英雄
力
度
增加
数量
```



## 描边

如果不同的字需要不同的描边效果，可以创建材质球，更改材质球的设置

<img class="half" src="/../images/unity/TMP字体/创建材质球.png"></img>

下面提供一个效果还不错的描边设置

<img class="half" src="/../images/unity/TMP字体/效果不错的描边.png"></img>





## 错误解决

```C#
The character used for Underline is not available in font asset [ZiYuYongSongTi-2 SDF].
```

当包如下警告时，说明字体里没有`_`下划线这个字符集，需要在创建字体的时候在Characters.txt中添加下划线。

如果已经添加了，或者使用的是动态的字体，则说明原本的ttf字体本身就没有`_`字符集

处理方法：

下载[FontCreator](https://www.high-logic.com/font-editor/fontcreator/download-confirmation)软件

File->Open->打开字体

<img class="half" src="/../images/unity/TMP字体/添加字符1.png"></img>

如果你不知道哪些字体中有下划线，或者你有心仪的字体的下划线，可以在随便添加一个字体后，从你指定的字体中复制一个下划线

<img class="half" src="/../images/unity/TMP字体/添加字符2.png"></img>

<img class="half" src="/../images/unity/TMP字体/添加字符3.png"></img>



## 原贴

[原贴](https://www.bilibili.com/opus/757765482578182153)
