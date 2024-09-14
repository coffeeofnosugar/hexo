---
title: 【Unity】Shader学习笔记-粒子效果自定义数据
date: 2024-09-10 00:49:06
tags:
  - Unity
  - Shader
---

### Shader制作

<img class="half" src="/../images/unity/Shader学习笔记-粒子效果/ScreenshotASE.png"></img>

这里需要注意的是：

- 粒子系统的参数并不是直接将float类型的数据来当做参数，而是将不同通道的UV当做参数
- 当做通道的参数需要将`UV Set`设置为非0

源码(删除掉了注释和预编译)：

```C#
Shader "CustomizeInformation_ASE"
{
	Properties
	{
		_MainTexture("MainTexture", 2D) = "white" {}
		_NoiseTexture("NoiseTexture", 2D) = "white" {}
		_DissolveTexture("DissolveTexture", 2D) = "white" {}
		[HideInInspector] _texcoord( "", 2D ) = "white" {}

	}
	
	SubShader
	{
		Tags { "RenderType"="Transparent" "Queue"="Transparent" }
	LOD 100

		CGINCLUDE
		#pragma target 3.0
		ENDCG
		Blend SrcAlpha OneMinusSrcAlpha
		AlphaToMask Off
		Cull Back
		ColorMask RGBA
		ZWrite Off
		ZTest LEqual
		Offset 0 , 0
		
		Pass
		{
			Name "Unlit"

			CGPROGRAM

			#pragma vertex vert
			#pragma fragment frag
			#pragma multi_compile_instancing
			#include "UnityCG.cginc"
			
			struct appdata
			{
				float4 vertex : POSITION;
				float4 color : COLOR;
				float4 ase_texcoord : TEXCOORD0;
				float4 ase_texcoord1 : TEXCOORD1;
				UNITY_VERTEX_INPUT_INSTANCE_ID
			};
			
			struct v2f
			{
				float4 vertex : SV_POSITION;
				float4 ase_texcoord1 : TEXCOORD1;
				float4 ase_texcoord2 : TEXCOORD2;
				UNITY_VERTEX_INPUT_INSTANCE_ID
				UNITY_VERTEX_OUTPUT_STEREO
			};

			uniform sampler2D _MainTexture;
			uniform float4 _MainTexture_ST;
			uniform sampler2D _NoiseTexture;
			uniform float4 _NoiseTexture_ST;
			uniform sampler2D _DissolveTexture;
			uniform float4 _DissolveTexture_ST;

			v2f vert ( appdata v )
			{
				v2f o;
				UNITY_SETUP_INSTANCE_ID(v);
				UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
				UNITY_TRANSFER_INSTANCE_ID(v, o);

				o.ase_texcoord1.xy = v.ase_texcoord.xy;
				o.ase_texcoord2 = v.ase_texcoord1;
				
				//setting value to unused interpolator channels and avoid initialization warnings
				o.ase_texcoord1.zw = 0;
				float3 vertexValue = float3(0, 0, 0);
				vertexValue = vertexValue;
				v.vertex.xyz += vertexValue;
				o.vertex = UnityObjectToClipPos(v.vertex);

				return o;
			}
			
			fixed4 frag (v2f i ) : SV_Target
			{
				UNITY_SETUP_INSTANCE_ID(i);
				UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
				fixed4 finalColor;
				float2 uv_MainTexture = i.ase_texcoord1.xy * _MainTexture_ST.xy + _MainTexture_ST.zw;
				float4 texCoord5 = i.ase_texcoord2;
				texCoord5.xy = i.ase_texcoord2.xy * float2( 1,1 ) + float2( 0,0 );
				float2 appendResult6 = (float2(texCoord5.x , texCoord5.y));
				float2 uv_NoiseTexture = i.ase_texcoord1.xy * _NoiseTexture_ST.xy + _NoiseTexture_ST.zw;
				float2 temp_cast_0 = (tex2D( _NoiseTexture, uv_NoiseTexture ).r).xx;
				float2 lerpResult7 = lerp( ( uv_MainTexture + appendResult6 ) , temp_cast_0 , texCoord5.z);
				float4 tex2DNode1 = tex2D( _MainTexture, lerpResult7 );
				float2 uv_DissolveTexture = i.ase_texcoord1.xy * _DissolveTexture_ST.xy + _DissolveTexture_ST.zw;
				float4 appendResult11 = (float4(tex2DNode1.rgb , ( tex2DNode1.a * step( texCoord5.w , tex2D( _DissolveTexture, uv_DissolveTexture ).r ) )));
				
				finalColor = appendResult11;
				return finalColor;
			}
			ENDCG
		}
	}
	Fallback Off
}
```



### 代码解析（使用反推法）：

1. 可以通过`lerp`函数看出来，`texCoord5`就是我们的UVSet=1

   ```C#
   fixed4 frag (v2f i ) : SV_Target
   {
       ...
   	float2 lerpResult7 = lerp( ( uv_MainTexture + appendResult6 ) , temp_cast_0 , texCoord5.z);
       ...
   }
   ```

2. 所以结构体`v2f`中的`ase_texcoord2`存储的就是UVSet=1

   ```C#
   fixed4 frag (v2f i ) : SV_Target
   {
       ...
   	float4 texCoord5 = i.ase_texcoord2;
       ...
   	float2 lerpResult7 = lerp( ( uv_MainTexture + appendResult6 ) , temp_cast_0 , texCoord5.z);
       ...
   }
   ```

3. **结构体`v2f`中的`ase_texcoord2`是从`appdata`的`ase_texcoord1`赋值过来的**

   ```C#
   v2f vert ( appdata v )
   {
       ...
       o.ase_texcoord2 = v.ase_texcoord1;
       ...
   }
   ```

4. **还需要注意到结构体`appdata`中的`ase_texcoord.zw`并没有被赋值<font color="DarkGray">（整个代码`ase_texcoord`只使用过一次）</font>**

   ```C#
   v2f vert ( appdata v )
   {
       ...
   	o.ase_texcoord1.xy = v.ase_texcoord.xy;
       ...
   }
   ```



### 粒子系统设置

1. 勾选`Custom Vertex Streams`并按顺序添加`UV2`和`Custom1.xyzw`

   - `UV2(TEXCOORD0.zw)`：初始化`appdata`中的`ase_texcoord.zw`，对应代码解析的第四步
   - `Custom1.xyzw(TEXCOORD1.xyzw)`：将下一步的`Custom1.xyzw`对应上`appdata`中的`ase_texcoord1`，对应代码解析的第三步

   ```C#
   struct appdata
   {
       float4 vertex : POSITION;
       float4 color : COLOR;
       float4 ase_texcoord : TEXCOORD0;
       float4 ase_texcoord1 : TEXCOORD1;
       UNITY_VERTEX_INPUT_INSTANCE_ID
   };
   ```

<img class="half" src="/../images/unity/Shader学习笔记-粒子效果/粒子系统设置-1.png"></img>

2. 启动`Custom Data`，并添加`Vector4`

<img class="half" src="/../images/unity/Shader学习笔记-粒子效果/粒子系统设置-2.png"></img>



### 使用自定义参数

<img class="half" src="/../images/unity/Shader学习笔记-粒子效果/效果展示.gif"></img>



### 测试

1. 经测试，U、V并不一定是只能控制X、Y方向的移动，可以控制其他数据。换句话说，这个节点已经与普通的UV坐标节点没有任何关系了，可以直接当做`Vector4`来使用。如下图连接，U控制流动，V控制透明，W、T控制X、Y方向的偏移

<img class="half" src="/../images/unity/Shader学习笔记-粒子效果/测试-1.png"></img>

2. 如果需要再添加一个参数，可以再添加一个UVSet=2的节点。并在粒子系统中添加`Custom2.xyzw(TEXCOORD2.xyzw)`。

<img class="half" src="/../images/unity/Shader学习笔记-粒子效果/测试-2.png"></img>

3. 也可以只用一个UV通道
   - 只有一个UV通道，U、V当做普通的UV坐标了，所以只能用W和T
   - 将`Custom1.x`映射到`TEXCOORD.z`上

<img class="half" src="/../images/unity/Shader学习笔记-粒子效果/测试-3.png"></img>



---

参考

[【Unity】【Amplify Shader Editor】ASE入门系列教程第十课 CustomData与顶点数据流](https://www.bilibili.com/video/BV1XT4y1v7ND/?share_source=copy_web&vd_source=880cf67fce3794b5c4a9039989704c6e)
