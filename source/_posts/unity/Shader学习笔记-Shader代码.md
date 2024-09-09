---
title: 【Unity】Shader学习笔记-Shader代码
date: 2024-09-10 00:49:06
tags:
  - Unity
  - Shader
---

### 结构

结合图形编辑器认识代码，下面是使用ASE制作的一个很简单的两个纹理相乘的Shader

<img class="half" src="/../images/unity/Shader学习笔记/SampleASE.png"></img>

```C#
Shader "New Amplify Shader"
{
	Properties
	{
		_TextureSample0("Texture Sample 0", 2D) = "white" {}	// 定义两个纹理
		_TextureSample1("Texture Sample 1", 2D) = "white" {}
	}
	
	SubShader		// 是Shader的核心，定义了渲染对象的方式
	{
		Tags { "RenderType"="Opaque" }		// 表示这个 Shader 用于渲染不透明对象
	LOD 100									// 表示细节层级，较低的值意味着较低的复杂度

        CGINCLUDE					// 在 CGINCLUDE 和 ENDCG 之间，定义了一些全局指令，用于控制着色器的目标平台
        #pragma target 3.0			// 表示支持的着色器模型
        ENDCG						// 结束定义全局指令
        Blend Off					// 关闭透明混合
        AlphaToMask Off				// 不使用 alpha 到掩码转换
        Cull Back					// 开启背面剔除，只渲染物体正面
        ColorMask RGBA				// 允许写入颜色的所有通道（红、绿、蓝、alpha）
        ZWrite On					// 开启深度写入，表示物体会写入深度缓冲区
        ZTest LEqual				// 使用深度测试，表示只渲染深度值小于或等于当前深度缓冲值的片段
        Offset 0 , 0				// 没有深度偏移
		
		Pass					// 每个 SubShader 可以有一个或多个渲染通道（Pass），表示渲染时应用不同的处理。
		{
			Name "Unlit"		// 这里使用了一个名字为 "Unlit" 的通道。

			CGPROGRAM
                
			#pragma vertex vert					// 指定顶点着色器函数是vert
			#pragma fragment frag				// 指定片段（像素）着色器函数是frag
			#pragma multi_compile_instancing	// 启用GPU实例化支持，用于优化同一对象的大量渲染
			#include "UnityCG.cginc"			// 包含 Unity 常用的 Cg 函数库，提供了常见的数学、纹理和其他实用函数
			
			struct appdata							// 代表顶点输入数据
			{
				float4 vertex : POSITION;			// 顶点的空间坐标
				float4 color : COLOR;				// 顶点颜色
				float4 ase_texcoord : TEXCOORD0;	// 第一个纹理坐标
				float4 ase_texcoord1 : TEXCOORD1;	// 第二个纹理
				UNITY_VERTEX_INPUT_INSTANCE_ID		// 用于GPU实例化支持
			};
			
			struct v2f								// 用于在顶点着色器和片段着色器之间传递数据
			{
				float4 vertex : SV_POSITION;			// 存储顶点的屏幕空间坐标
				#ifdef ASE_NEEDS_FRAG_WORLD_POSITION
				float3 worldPos : TEXCOORD0;
				#endif
				float4 ase_texcoord1 : TEXCOORD1;		// 存储纹理坐标，TEXCOORD1表示这是该顶点对应的第二组纹理坐标
				UNITY_VERTEX_INPUT_INSTANCE_ID			// 支持实例化渲染
				UNITY_VERTEX_OUTPUT_STEREO				// 支持VR渲染
			};

			uniform sampler2D _TextureSample0;
			uniform sampler2D _TextureSample1;

			v2f vert ( appdata v )
			{
				v2f o;
				// 这些宏是 Unity 提供的，用于支持实例化和虚拟现实渲染。
				UNITY_SETUP_INSTANCE_ID(v);
				UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
				UNITY_TRANSFER_INSTANCE_ID(v, o);

                o.ase_texcoord1.xy = v.ase_texcoord.xy;		// 将输入的第一组纹理坐标赋值给输出
                o.ase_texcoord1.zw = v.ase_texcoord1.xy;	// 将第二组纹理坐标赋给输出
                float3 vertexValue = float3(0, 0, 0);
                vertexValue = vertexValue;
                v.vertex.xyz += vertexValue;
                o.vertex = UnityObjectToClipPos(v.vertex);	// 将顶点转换为屏幕坐标系，以便在片段着色器中进行渲染。
                return o;
			}
			
			fixed4 frag (v2f i ) : SV_Target
			{
				UNITY_SETUP_INSTANCE_ID(i);
				UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
    			// 从ase_texcoord1的前两项（xy）获取纹理坐标
				fixed4 finalColor;
    			// 从ase_texcoord1的前两项（xy）获取纹理坐标
				float2 texCoord1 = i.ase_texcoord1.xy * float2( 1,1 ) + float2( 0,0 );
    			// // 从ase_texcoord1的后两项（zw）获取纹理坐标
				float2 texCoord3 = i.ase_texcoord1.zw * float2( 1,1 ) + float2( 0,0 );
				
    			// 取出颜色值后，将两个纹理的颜色相乘，生成最终的颜色
				finalColor = ( tex2D( _TextureSample0, texCoord1 ) * tex2D( _TextureSample1, texCoord3 ) );
				return finalColor;
			}
			ENDCG
		}
	}
	CustomEditor "ASEMaterialInspector"
	
	Fallback Off
}
```



#### Properties

```c#
Properties
{
    _TextureSample0("Texture Sample 0", 2D) = "white" {}	// 定义两个纹理
    _TextureSample1("Texture Sample 1", 2D) = "white" {}
}
```

定义了两个 2D 纹理，可以在Inspector上修改参数



#### SubShader

```C#
SubShader
{
    Tags { "RenderType"="Opaque" }		// 表示这个 Shader 用于渲染不透明对象
    LOD 100								// 表示细节层级，较低的值意味着较低的复杂度
    ...
    Pass
    {
        Name "Unlit"
        CGPROGRAM
        ...
        ENDCG
    }
}
```

每个 `SubShader` 可以有一个或多个渲染通道（Pass），表示渲染时应用不同的处理。这里使用了一个名字为 "Unlit" 的通道。



#### CGINCLUDE 和 渲染状态设置

```C#
CGINCLUDE					// 在 CGINCLUDE 和 ENDCG 之间，定义了一些全局指令，用于控制着色器的目标平台
#pragma target 3.0			// 表示支持的着色器模型
ENDCG						// 结束定义全局指令
Blend Off					// 关闭透明混合
AlphaToMask Off				// 不使用 alpha 到掩码转换
Cull Back					// 开启背面剔除，只渲染物体正面
ColorMask RGBA				// 允许写入颜色的所有通道（红、绿、蓝、alpha）
ZWrite On					// 开启深度写入，表示物体会写入深度缓冲区
ZTest LEqual				// 使用深度测试，表示只渲染深度值小于或等于当前深度缓冲值的片段
Offset 0 , 0				// 没有深度偏移
```



#### Vertex 和 Fragment的定义

```c#
#pragma vertex vert					// 指定顶点着色器函数是vert
#pragma fragment frag				// 指定片段（像素）着色器函数是frag
#pragma multi_compile_instancing	// 启用GPU实例化支持，用于优化同一对象的大量渲染
#include "UnityCG.cginc"			// 包含 Unity 常用的 Cg 函数库，提供了常见的数学、纹理和其他实用函数
```



#### 顶点着色器 (Vertex Shader)

```c#
struct appdata							// 代表顶点输入数据
{
    float4 vertex : POSITION;			// 顶点的空间坐标
    float4 color : COLOR;				// 顶点颜色
    float4 ase_texcoord : TEXCOORD0;	// 第一个纹理坐标
	float4 ase_texcoord1 : TEXCOORD1;	// 第二个纹理
	UNITY_VERTEX_INPUT_INSTANCE_ID		// 用于GPU实例化支持
};
```

`appdata` 结构体代表顶点输入数据，它包含：

- **vertex**: 顶点的空间坐标。
- **color**: 顶点颜色。
- **ase_texcoord / ase_texcoord1**: 两个纹理坐标。
- **UNITY_VERTEX_INPUT_INSTANCE_ID**: 用于 GPU 实例化支持。

```C#
v2f vert (appdata v)
{
    v2f o;
    
    // 这些宏是 Unity 提供的，用于支持实例化和虚拟现实渲染。
    UNITY_SETUP_INSTANCE_ID(v);
    UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
    UNITY_TRANSFER_INSTANCE_ID(v, o);

    o.ase_texcoord1.xy = v.ase_texcoord.xy;		// 将输入的第一组纹理坐标赋值给输出
    o.ase_texcoord1.zw = v.ase_texcoord1.xy;	// 将第二组纹理坐标赋给输出
    float3 vertexValue = float3(0, 0, 0);
    vertexValue = vertexValue;
    v.vertex.xyz += vertexValue;
    o.vertex = UnityObjectToClipPos(v.vertex);	// 将顶点转换为屏幕坐标系，以便在片段着色器中进行渲染。
    return o;
}

```



#### 片段着色器 (Fragment Shader)

```C#
struct v2f								// 用于在顶点着色器和片段着色器之间传递数据
{
    float4 vertex : SV_POSITION;			// 存储顶点的屏幕空间坐标
    float4 ase_texcoord1 : TEXCOORD1;		// 存储纹理坐标，TEXCOORD1表示这是该顶点对应的第二组纹理坐标
    UNITY_VERTEX_INPUT_INSTANCE_ID			// 支持实例化渲染
    UNITY_VERTEX_OUTPUT_STEREO				// 支持VR渲染
};
```

- `SV_POSITION` ：表示该值是顶点的最终位置，经过模型-视图-投影矩阵变换后，在屏幕坐标系中的位置。
- `TEXCOORD1` ：表示这是该顶点对应的第二组纹理坐标。
- `UNITY_VERTEX_INPUT_INSTANCE_ID`：支持实例化渲染，如果你在场景中绘制多个相同的对象（实例化渲染），这个宏会确保每个实例都有唯一的标识符，使得每个对象在渲染时可以被区分开。
- `UNITY_VERTEX_OUTPUT_STEREO`：用于支持虚拟现实（VR）渲染，它确保在 VR 渲染中，输出适应双眼视图（左右眼分别渲染），从而生成立体图像。

```C#
fixed4 frag (v2f i ) : SV_Target
{
    fixed4 finalColor;
    // 从ase_texcoord1的前两项（xy）获取纹理坐标
    float2 texCoord1 = i.ase_texcoord1.xy * float2( 1,1 ) + float2( 0,0 );
    // // 从ase_texcoord1的后两项（zw）获取纹理坐标
    float2 texCoord3 = i.ase_texcoord1.zw * float2( 1,1 ) + float2( 0,0 );

    // 取出颜色值后，将两个纹理的颜色相乘，生成最终的颜色
    finalColor = ( tex2D( _TextureSample0, texCoord1 ) * tex2D( _TextureSample1, texCoord3 ) );
    return finalColor;
}
```

- `texCoord1` 和 `texCoord3`：分别使用 `ase_texcoord1` 的前两项（`xy`）和后两项（`zw`）来获取两个纹理的纹理坐标。

- `tex2D(_TextureSample0, texCoord1)`：根据纹理坐标 `texCoord1` 从纹理 `_TextureSample0` 中取出颜色值。
- `tex2D(_TextureSample1, texCoord3)`：根据纹理坐标 `texCoord3` 从纹理 `_TextureSample1` 中取出颜色值。
- `finalColor = tex2D( _TextureSample0, texCoord1 ) * tex2D( _TextureSample1, texCoord3 )`：将两个纹理的颜色值相乘，生成最终的颜色。
- 最终返回 `finalColor`，作为当前像素的颜色值。



### 源码

```C#
// Made with Amplify Shader Editor v1.9.6.3
// Available at the Unity Asset Store - http://u3d.as/y3X 
Shader "New Amplify Shader"
{
	Properties
	{
		_TextureSample0("Texture Sample 0", 2D) = "white" {}
		_TextureSample1("Texture Sample 1", 2D) = "white" {}

	}
	
	SubShader
	{
		
		
		Tags { "RenderType"="Opaque" }
	LOD 100

		CGINCLUDE
		#pragma target 3.0
		ENDCG
		Blend Off
		AlphaToMask Off
		Cull Back
		ColorMask RGBA
		ZWrite On
		ZTest LEqual
		Offset 0 , 0
		
		
		
		Pass
		{
			Name "Unlit"

			CGPROGRAM

			

			#ifndef UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX
			//only defining to not throw compilation error over Unity 5.5
			#define UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input)
			#endif
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
				#ifdef ASE_NEEDS_FRAG_WORLD_POSITION
				float3 worldPos : TEXCOORD0;
				#endif
				float4 ase_texcoord1 : TEXCOORD1;
				UNITY_VERTEX_INPUT_INSTANCE_ID
				UNITY_VERTEX_OUTPUT_STEREO
			};

			uniform sampler2D _TextureSample0;
			uniform sampler2D _TextureSample1;

			
			v2f vert ( appdata v )
			{
				v2f o;
				UNITY_SETUP_INSTANCE_ID(v);
				UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
				UNITY_TRANSFER_INSTANCE_ID(v, o);

				o.ase_texcoord1.xy = v.ase_texcoord.xy;
				o.ase_texcoord1.zw = v.ase_texcoord1.xy;
				float3 vertexValue = float3(0, 0, 0);
				#if ASE_ABSOLUTE_VERTEX_POS
				vertexValue = v.vertex.xyz;
				#endif
				vertexValue = vertexValue;
				#if ASE_ABSOLUTE_VERTEX_POS
				v.vertex.xyz = vertexValue;
				#else
				v.vertex.xyz += vertexValue;
				#endif
				o.vertex = UnityObjectToClipPos(v.vertex);

				#ifdef ASE_NEEDS_FRAG_WORLD_POSITION
				o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
				#endif
				return o;
			}
			
			fixed4 frag (v2f i ) : SV_Target
			{
				UNITY_SETUP_INSTANCE_ID(i);
				UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(i);
				fixed4 finalColor;
				#ifdef ASE_NEEDS_FRAG_WORLD_POSITION
				float3 WorldPosition = i.worldPos;
				#endif
				float2 texCoord1 = i.ase_texcoord1.xy * float2( 1,1 ) + float2( 0,0 );
				float2 texCoord3 = i.ase_texcoord1.zw * float2( 1,1 ) + float2( 0,0 );
				
				
				finalColor = ( tex2D( _TextureSample0, texCoord1 ) * tex2D( _TextureSample1, texCoord3 ) );
				return finalColor;
			}
			ENDCG
		}
	}
	CustomEditor "ASEMaterialInspector"
	
	Fallback Off
}
/*ASEBEGIN
Version=19603
Node;AmplifyShaderEditor.TextureCoordinatesNode;1;-816,-32;Inherit;False;0;-1;2;3;2;SAMPLER2D;;False;0;FLOAT2;1,1;False;1;FLOAT2;0,0;False;5;FLOAT2;0;FLOAT;1;FLOAT;2;FLOAT;3;FLOAT;4
Node;AmplifyShaderEditor.TextureCoordinatesNode;3;-800,208;Inherit;False;1;-1;2;3;2;SAMPLER2D;;False;0;FLOAT2;1,1;False;1;FLOAT2;0,0;False;5;FLOAT2;0;FLOAT;1;FLOAT;2;FLOAT;3;FLOAT;4
Node;AmplifyShaderEditor.SamplerNode;2;-528,-48;Inherit;True;Property;_TextureSample0;Texture Sample 0;0;0;Create;True;0;0;0;False;0;False;-1;None;None;True;0;False;white;Auto;False;Object;-1;Auto;Texture2D;8;0;SAMPLER2D;;False;1;FLOAT2;0,0;False;2;FLOAT;0;False;3;FLOAT2;0,0;False;4;FLOAT2;0,0;False;5;FLOAT;1;False;6;FLOAT;0;False;7;SAMPLERSTATE;;False;6;COLOR;0;FLOAT;1;FLOAT;2;FLOAT;3;FLOAT;4;FLOAT3;5
Node;AmplifyShaderEditor.SamplerNode;4;-528,176;Inherit;True;Property;_TextureSample1;Texture Sample 1;1;0;Create;True;0;0;0;False;0;False;-1;None;None;True;0;False;white;Auto;False;Object;-1;Auto;Texture2D;8;0;SAMPLER2D;;False;1;FLOAT2;0,0;False;2;FLOAT;0;False;3;FLOAT2;0,0;False;4;FLOAT2;0,0;False;5;FLOAT;1;False;6;FLOAT;0;False;7;SAMPLERSTATE;;False;6;COLOR;0;FLOAT;1;FLOAT;2;FLOAT;3;FLOAT;4;FLOAT3;5
Node;AmplifyShaderEditor.SimpleMultiplyOpNode;5;-192,64;Inherit;False;2;2;0;COLOR;0,0,0,0;False;1;COLOR;0,0,0,0;False;1;COLOR;0
Node;AmplifyShaderEditor.TemplateMultiPassMasterNode;0;0,0;Float;False;True;-1;2;ASEMaterialInspector;100;5;New Amplify Shader;0770190933193b94aaa3065e307002fa;True;Unlit;0;0;Unlit;2;False;True;0;1;False;;0;False;;0;1;False;;0;False;;True;0;False;;0;False;;False;False;False;False;False;False;False;False;False;True;0;False;;False;True;0;False;;False;True;True;True;True;True;0;False;;False;False;False;False;False;False;False;True;False;0;False;;255;False;;255;False;;0;False;;0;False;;0;False;;0;False;;0;False;;0;False;;0;False;;0;False;;False;True;1;False;;True;3;False;;True;True;0;False;;0;False;;True;1;RenderType=Opaque=RenderType;True;2;False;0;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;False;0;;0;0;Standard;1;Vertex Position,InvertActionOnDeselection;1;0;0;1;True;False;;False;0
WireConnection;2;1;1;0
WireConnection;4;1;3;0
WireConnection;5;0;2;0
WireConnection;5;1;4;0
WireConnection;0;0;5;0
ASEEND*/
//CHKSM=8216CF2D2690911483A0CC9FD37960BE3735D58B
```









