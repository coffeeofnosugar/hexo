---
title: 【Unity】Shader学习笔记-PostProcessing
date: 2024-09-02 16:50:06
mathjax: true
tags:
  - Unity
  - Shader
---

### 坑

记一次unity后处理大坑，耗费了我整整一天的时间碰壁，可以说基本上是把里面能踩的坑全踩了

这一天来踩的坑如下：

1. ASE插件的Post-Processing Stack Tool生成的后处理脚本不支持URP<font color="DarkGray">（客服说预计年底能支持URP）</font>

<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/坑1.png"></img>

2. Post Processing插件不支持URP，URP只能使用Volume来实现后处理效果<font color="DarkGray">（这条是坑1的根本原因）</font>

<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/坑2.png"></img>

3. PostProcessing插件的组件应该挂载在相机上才能正常工作
4. 和PostProcessing一样，Volume同样也给了用户自定义的方法，但是比PostProcessing麻烦太多<font color="DarkGray">（这个坑花费了我最多时间）</font>

4. 在配置管线(`Universal Render Pipeline Asset`)的时候不能简单的新创建一个`URP Asset_Render`直接添加到`Renderer List`的后面，这样设置并不起效。如果不知道该如何添加`Renderer List`，最简单的方法就是使用默认的`URP Asset_Render`
5. 在自定义`Volume`的时候`VolumeComponent `得放在一个单独的文件下，不然会警告找不到这个类
6. 在自定义`Volume`的时候使用的`RenderTargetHandle`和`Blit()`时Unity会警告提示过时，应该使用`RTHandle`和`Blitter.BlitCameraTexture()`。但是如果你只是简单的更换这些属性和方法，最终游戏中并不会实现你编写的Shader效果，因为`Blitter.BlitCameraTexture()`不支持`Core.hlsl`，得使用`Blit.hlsl`



<img class="half" src="/../images/common/表情包/汉.jpg"></img>

诶，一天下来能碰到这么多坑也是没谁了。



---

### 参考

还是感谢网络上各位大佬的无私分享，参考：

[Fade In Out Post Process Shader](https://wiki.amplify.pt/index.php?title=Unity_Products:Amplify_Shader_Editor/Tutorials/Fade_In_Out_Post_Process_Shader)

[《Unity Shader 入门精要》从Bulit-in 到URP （HLSL）之后处理（Post-processing : RenderFeature + VolumeComponent）](https://zhuanlan.zhihu.com/p/572652890)

[Unity URP 自定义RendererFeature笔记](https://zhuanlan.zhihu.com/p/675758658)

[Create A Custom URP Post Effect In Unity](https://www.youtube.com/watch?v=oLyv3NSpPeg)

[Custom Post Processing In Urp](https://www.febucci.com/2022/05/custom-post-processing-in-urp/)

[既存のRendererFeatureをURP14のBlitに対応させる](https://zenn.dev/sakutaro/articles/convert_blitter)

[(URP 13.1.8) Proper RTHandle usage in a Renderer Feature](https://discussions.unity.com/t/urp-13-1-8-proper-rthandle-usage-in-a-renderer-feature/895405)



---

### URP实现PostProcessing

最终还是[《Unity Shader 入门精要》从Bulit-in 到URP （HLSL）之后处理（Post-processing : RenderFeature + VolumeComponent）](https://zhuanlan.zhihu.com/p/572652890)扒取了这篇文章的代码实现了简单的效果。其根据我自己的理解简化了代码，使代码更清晰



#### `VolumeComponent`

首先是`VolumenComponent`，继承这个类之后就能在`Volume`组件上`AddOverride`。

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/VolumeComponent-1.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/VolumeComponent-2.png"></img>

{% endgrouppicture %}

```c#
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

[System.Serializable, VolumeComponentMenu("Ding Post-processing/Test")]
public class CustomVolumeComponent : VolumeComponent, IPostProcessComponent
{
    public MinFloatParameter Brightness = new MinFloatParameter(1f, 0);//只有使用特定的数值类才能显示到Inspector上
    public ClampedFloatParameter Saturation = new ClampedFloatParameter(1f, 0, 1f);
    public ClampedFloatParameter Contrast = new ClampedFloatParameter(1f, 0, 1f);
    public bool IsActive() => true;
    public bool IsTileCompatible() => false;
}
```



#### `DingRenderPassFeature`

这里的两个类`RenderPassFeature`和`RenderPass`可以分开写，但是他们两是依赖关系。

并且如果将`RenderPass`放在外面的话，还要重命名，所以我个人倾向不分开

```C#
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public class DingRenderPassFeature : ScriptableRendererFeature
{
    class CustomRenderPass : ScriptableRenderPass
    {
        private Material material;
        private RTHandle source;
        private RenderTargetHandle tempTexture;
        
        string m_ProfilerTag = nameof(DingRenderPassFeature);
        private CustomVolumeComponent volume;

        public CustomRenderPass(Shader shader, RenderPassEvent renderPassEvent)
        {
            if(shader == null) return;
            
            material = CoreUtils.CreateEngineMaterial(shader);
            
            this.renderPassEvent = renderPassEvent;
            
            var stack = VolumeManager.instance.stack;
            volume = stack.GetComponent<CustomVolumeComponent>();
        }

        public override void OnCameraSetup(CommandBuffer cmd, ref RenderingData renderingData)
        {
            source = renderingData.cameraData.renderer.cameraColorTargetHandle;
        }

        public override void Execute(ScriptableRenderContext context, ref RenderingData renderingData)
        {
            if (material is null) return;
            
            // 设置m_ProfilerTag之后，在FrameDebugger上就可以更具这个名称来搜索（设置成其他名字也可以，但是为了对应上管线设置，还是设置成PassFeature方便观察）
            CommandBuffer cmd = CommandBufferPool.Get(m_ProfilerTag);
            
            material.SetFloat("_Brightness", volume.Brightness.value);
            material.SetFloat("_Saturation", volume.Saturation.value);
            material.SetFloat("_Contrast", volume.Contrast.value);

            RenderTextureDescriptor desc = renderingData.cameraData.cameraTargetDescriptor;
            desc.depthBufferBits = 0;
            desc.msaaSamples = 1;
            
            cmd.GetTemporaryRT(tempTexture.id, desc);
            Blit(cmd, source, tempTexture.Identifier(), material, 0);
            Blit(cmd, tempTexture.Identifier(), source);
            cmd.ReleaseTemporaryRT(tempTexture.id);
            
            // 如果不希望看到过时警告就使用这个，但是对应的Shader也要改成支持Blit.hlsl的
            // Blitter.BlitCameraTexture(cmd, source, source, material, 0);
        
            context.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
        }

        public override void OnCameraCleanup(CommandBuffer cmd)
        {
            
        }
    }

    [System.Serializable]
    public class Settings{
        public RenderPassEvent Event = RenderPassEvent.AfterRenderingTransparents;
        public Shader shader;
    }

    public Settings settings = new Settings();
    CustomRenderPass m_ScriptablePass;

    public override void Create()
    {
        m_ScriptablePass = new CustomRenderPass(settings.shader, settings.Event);
    }

    public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
    {
        if (settings.shader is null) return;
        
        renderer.EnqueuePass(m_ScriptablePass);
    }
}
```



#### `Shader`

```
Shader "Unlit/Chapter12-BrightnessSaturationAndContrast"
{
    Properties {
		_MainTex ("Base (RGB)", 2D) = "white" {}
		_Brightness ("Brightness", Float) = 1.5
		_Saturation("Saturation", Float) = 1.5
		_Contrast("Contrast", Float) = 1.5
	}
    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" }
        ZTest Always Cull Off ZWrite Off
        //基本是后处理shader的必备设置，放置场景中的透明物体渲染错误
//注意进行该设置后，shader将在完成透明物体的渲染后起作用，即RenderPassEvent.AfterRenderingTransparents后

        Pass
        {
			HLSLPROGRAM 
			#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
			#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
			#include "Packages/com.unity.render-pipelines.core/Runtime/Utilities/Blit.hlsl"
			
			#pragma vertex vert
			#pragma fragment frag

            CBUFFER_START(UnityPerMaterial)
            half _Brightness;
			half _Saturation;
			half _Contrast;
            CBUFFER_END

            TEXTURE2D(_MainTex);       SAMPLER(sampler_MainTex);

            struct a2v{
                float4 vertex : POSITION;
				float4 texcoord : TEXCOORD0;
            };

            struct v2f {
				float4 pos : SV_POSITION;
				half2 uv: TEXCOORD0;
			};
			  
			v2f vert(a2v v) {
                //appdata_img在URP下不能使用，保险起见自己定义输入结构体
                v2f o;
				
				o.pos = TransformObjectToHClip(v.vertex);
				
				o.uv = v.texcoord;
						 
				return o;
			}
		
			half4 frag(v2f i) : SV_Target {
				half4 renderTex = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, i.uv); 
				  
				// Apply brightness
				half3 finalColor = renderTex.rgb * _Brightness;
                //亮度的调整非常简单，只需要把原颜色乘以亮度系数_Brightness即可
				
				// Apply saturation
				half luminance = 0.2125 * renderTex.r + 0.7154 * renderTex.g + 0.0721 * renderTex.b;
				half3 luminanceColor = half3(luminance, luminance, luminance);
                //通过对每个颜色分量乘以一个特定的系数再相加得到一个饱和度为0的颜色值
				finalColor = lerp(luminanceColor, finalColor, _Saturation);
                //用_Saturation属性和上一步得到的颜色之间进行插值
				
				// Apply contrast
				half3 avgColor = half3(0.5, 0.5, 0.5);
                //创建一个对比度为0的颜色值（各分量均为0.5）
				finalColor = lerp(avgColor, finalColor, _Contrast);
                //使用_Contrast属性和上一步得到的颜色之间进行插值
				
				return half4(finalColor, renderTex.a);  
			}  
			  
			ENDHLSL
		}  
	}
    FallBack "Packages/com.unity.render-pipelines.universal/FallbackError"
}
```



#### 设置

代码都准备好后就可以设置了

1. 找到当前项目正在使用的管线设置

2. 然后添加我们自定义的渲染规则（名称就是`RenderPassFeature`的类名）
3. 添加shader



<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/URP设置-1.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/URP设置-2.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/URP设置-3.png"></img>



4. 添加Volume组件，并创建一个预设
5. 按照`VolumeComponent`添加volume



<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/URP设置-4.png"></img>

<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/URP设置-5.png"></img>





---

### 总结

最后实现起来其实并不难，步骤也不是很多。但其中的坑实在是太多了，耽搁了很多时间。

遗憾的是现在的我对Shader的操作现在还暂时停留在图形编辑，Shader代码还不怎么会。ASE生成的Shader也不支持URP的后期处理，所以暂时还无法消除代码中的过期警告。后续学习了如何编写Shader代码之后再来解决这个问题吧。

```C#
Assets\Volume\Scripts\SourceCode1\DingRenderPassFeature.cs(11,17): warning CS0618: 'RenderTargetHandle' is obsolete: 'Deprecated in favor of RTHandle'
```





---

### 后记：

突然记起来，之前在unity官方教程中学习过后处理的一点方法，如果只是简单的想要将Shader应用到场景中的物体上，可以按照[Shader Graph 遮挡剔除](https://learn.u3d.cn/tutorial/3drpg-core?chapterId=63562b29edca72001f21d19d#5fdb3f8a5a9d57002292df9b)的方法不使用代码直接将Shader应用到物体上。

具体做法：

在URP_Asset_Renderer上添加`Render Objects(Experimental)`，然后设置相应的名称、渲染时机、应用到物体的Layer、需要使用的材质。其他的具体设置可以点击上方的帮助查看官方文档

<img class="half" src="/../images/unity/Shader学习笔记-PostProcessing/后记.png"></img>







