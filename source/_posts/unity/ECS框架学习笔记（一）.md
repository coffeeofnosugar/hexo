---
title: 【Unity】ECS框架学习笔记（一）
date: 2024-09-15 07:11:06
tags:
  - Unity
---

### 安装

创建一个Unity项目

#### 包体

使用`Add the package by its name`添加以下模块

- `com.unity.entities`：包本体
- `com.unity.entities.graphics`：可使用脚本渲染管道(SRP)渲染实体
- `com.unity.physics`：实体的状态和物理系统

#### 环境

需要注意的是，IDE只能使用以下两种

- Visual Studio 2022+
- Rider 2021.3.3+

#### 版本

- Entities：1.2.4
- Entities Graphics：1.2.4
- Unity Physics：1.2.4



---

### 注意事项

#### Component

由于ECS中的C是**结构体**，在引用其内部数据的时候要注意引用的是其本体还是复制副本

#### Build

在build之前，执行以下操作确保Build成功

1. 关闭Entity子场景，这样在editor中将优先加载子场景。运行游戏时可能会遇到报错，例如在`OnCreate()`和`OnUpdate()`中获取单例就会报错
   - 原因：游戏在第一帧时子场景还没有加载完，所以单例不存在
   - 解决方法：在`OnCreate()`中添加`RequireForUpdate<T>`
   - 如果不希望每帧都调用单例，可以在`OnStartRunning()`中调用单例，这方法只适用`SystemBase`，因为`ISystem`没有该方法
2. Resolve Loading Entity Scene Failed errors，解决加载Entity Scene失败错误
   - 貌似是Unity的Bug
   - 可以重启Unity Editor，清除实体缓存。Edit-Preferences-Entities-ClearEntityCache
3. 保存主场景和子场景







---

### 示例：控制角色移动

#### 场景搭建

1. 创建子场景

   <img class="half" src="/../images/unity/ECS框架学习笔记/创建子场景.png"></img>

2. 创建Entities对象

   <img class="half" src="/../images/unity/ECS框架学习笔记/创建Entities对象.png"></img>



#### 脚本

- Component脚本：存放数据

  ```C#
  public struct Speed : IComponentData		// 存储角色移动速度
  {
  	public float value;
  }
  ```

  ```C#
  public struct TargetPosition : IComponentData		// 存储目标位置
  {
  	public float3 value;
  }
  ```

  

- Entities脚本：挂载到Entities上，将数据传递给Entities

  ```C#
  public class SpeedAuthoring : MonoBehaviour
  {
  	public float value;
  
  	public class SpeedBaker : Baker<SpeedAuthoring>
  	{
          // Debug.Log("Bake SpeedAuthoring");
  		public override void Bake(SpeedAuthoring authoring)
  		{
  			var entity = GetEntity(TransformUsageFlags.Dynamic);
  			var data = new Speed
  			{
  				value = authoring.value
  			};
  			AddComponent(entity, data);
  		}
  	}
  }
  ```

  ```c#
  public class TargetPositionAuthoring : MonoBehaviour
  {
  	public float3 value;
  	
  	public class Baker : Baker<TargetPositionAuthoring>
  	{
  		public override void Bake(TargetPositionAuthoring authoring)
  		{
  			var entity = GetEntity(TransformUsageFlags.Dynamic);
  			var data = new TargetPosition
  			{
  				value = authoring.value
  			};
  			AddComponent(entity, data);
  		}
  	}
  }
  ```

  注意一下烘焙时机，虽然可能不会用到

  <img class="half" src="/../images/unity/ECS框架学习笔记/烘焙时机.png"></img>

  

- System脚本：执行游戏逻辑

  ```C#
  public partial class MovingSystemBase : SystemBase
  {
  	protected override void OnUpdate()
  	{
  		foreach (var (localTransform, speed, targetPosition) in SystemAPI.Query<RefRW<LocalTransform>, RefRW<Speed>, RefRW<TargetPosition>>())
  		{
  			var direction = math.normalize(targetPosition.ValueRW.value - localTransform.ValueRW.Position);
  			localTransform.ValueRW.Position += direction * SystemAPI.Time.DeltaTime * speed.ValueRO.value;
  		}
  	}
  }
  ```
  



---

### 窗口介绍

<img class="half" src="/../images/unity/ECS框架学习笔记/调试窗口.png"></img>

- Systems

  - Entity Count：该system涉及到的实体，如：

    - 符合`ISystem.IJobEntity.Execute()`参数`IComponentData`或`IAspect`条件的实体

    - 在该system中使用过该实体的方法，如

      ```
      var entityCommandBuffer = SystemAPI.GetSingleton<BeginSimulationEntityCommandBufferSystem.Singleton>()
          .CreateCommandBuffer(World.Unmanaged);
      ```

    <img class="half" src="/../images/unity/ECS框架学习笔记/调试窗口.png"></img>



---

### System

#### IAspect

上面的System脚本是否看起来十分臃肿，可以使用`IAspect`将下达命令的System与执行逻辑分开。

除了能解耦执行逻辑外，还可以很清楚区分开该实体是否需要处理此执行逻辑。如下面的`MoveToPositionAspect`使用了`LocalTransform`、`Speed`和`TargetPosition`三个标签Component，那么所有拥有这三个的实体就执行此逻辑，少了任何一个都无法执行

> - `IAspect`同样是**结构体**，在使用时需要注意值类型和引用类型的问题
>
> - `IAspect`的Component字段只能是`RefRW`、`RefRO`、`EnabledRefRW`、`EnabledRefRO`、`DynamicBuffer` 或 `Entity`。
>   `Ref`正如关键字`ref`一样，直接引用其地址，而不是复制，这样就能避免值类型和引用类型的问题
> - 可以将`IAspect`看做是特殊的`IComponentData`，所有拥有其定义的`Ref`字段的实体就拥有该`IAspect`

```C#
public readonly partial struct MoveToPositionAspect : IAspect
{
	readonly RefRW<LocalTransform> localTransform;		// 可读可写
	readonly RefRO<Speed> speed;						// 只读
	readonly RefRW<TargetPosition> targetPosition;

	public void Move(float deltaTime)
	{
		var direction = math.normalize(targetPosition.ValueRW.value - localTransform.ValueRW.Position);
		localTransform.ValueRW.Position += direction * deltaTime * speed.ValueRO.value;
	}
}
```

将上面的`MovingSystemBase`修改为：

```C#
public partial class MovingSystemBase : SystemBase
{
	protected override void OnUpdate()
	{
		foreach (MoveToPositionAspect aspect in SystemAPI.Query<MoveToPositionAspect>())
		{
			aspect.Move(SystemAPI.Time.DeltaTime);
		}
	}
}
```

> 需要注意的是，`SystemAPI`只能在System中使用，所以只能将`DeltaTime`当做参数传递过去



#### ISystem

除了上面的`SystemBase`外还可以使用`ISystem`实现，`ISystem`更加轻量

因为是**结构体**，所以速度更快，但是和Component同样在使用时需要注意值类型和引用类型的问题

```C#
public partial struct MovingSystem : ISystem
{
	public void OnCreate(ref SystemState state) { }
	public void OnDestroy(ref SystemState state) { }
	public void OnUpdate(ref SystemState state)			// 与上面的SystemBase代码完全相同
	{
		foreach (MoveToPositionAspect aspect in SystemAPI.Query<MoveToPositionAspect>())
		{
			aspect.Move(SystemAPI.Time.DeltaTime);
		}
	}
}
```

- 实体很多就使用ISystem
- 不用在性能表现就使用SystemBase



#### `IJobEntity`异步`Burst`编译

将逻辑放在其他线程上，不阻塞主线程，引入`IJobEntity`的结构体

```C#
[BurstCompile]
public partial struct MovingISystem : ISystem
{
    [BurstCompile]
	public void OnCreate(ref SystemState state) { }
    [BurstCompile]
	public void OnDestroy(ref SystemState state) { }
    [BurstCompile]
	public void OnUpdate(ref SystemState state)
	{
		// foreach (MoveToPositionAspect aspect in SystemAPI.Query<MoveToPositionAspect>())	// 需要删除掉遍历
		// {
			var deltaTime = SystemAPI.Time.DeltaTime;
			// aspect.Move(deltaTime);
			
			Debug.Log($"MovingISystem ThreadId: {System.Threading.Thread.CurrentThread.ManagedThreadId}");
			
			JobHandle jobHandle = new MoveJob()
			{
				deltaTime = SystemAPI.Time.DeltaTime
			}.ScheduleParallel(state.Dependency);		// 异步并行，调到其他线程上执行
			
			jobHandle.Complete();		// 等待所有任务完成，再执行后面的代码，类似await，也就是说会在主线程上运行
			
			// Do Something...
		// }
	}
}

[BurstCompile]
public partial struct MoveJob : IJobEntity
{
    [NativeDisableUnsafePtrRestriction]
    public RefRO<Speed> speed;		// 在IJobEntity中调用`RefRo<>`或`RefRW<>`时会报错："不允许使用非安全指针，可能会崩溃"。如果你知道自己在做什么并且没有乱用指针可以使用属性关闭报错
    public float deltaTime;

    // 通过该方法的虚参来获取符合条件的实体，所以上面的foreach遍历是多余的
    [BurstCompile]
    public void Execute(MoveToPositionAspect aspect)
    {
        Debug.Log($"MoveJob ThreadId: {System.Threading.Thread.CurrentThread.ManagedThreadId}");
        aspect.Move(deltaTime);
    }
}
```

##### 线程ID

按照上面的代码运行了很多次，都是在4线程，说明`ScheduleParallel`并不是随机分配线程ID

<img class="half" src="/../images/unity/ECS框架学习笔记/线程-1.png"></img>

但是也有一个奇怪的现象，如果注释掉主线程的`Debug.Log()`，MoveJob ThreadId不止为4
原因应该与`UnityEngine`方法只能在主线程上执行有关，`Debug.Log()`为`UnityEngine`<font color="DarkGray">（Unity可能对该方法做了特殊处理，所以可以在其他线程上运行，但是输出的内容就不能考究了，尤其是涉及了线程）</font>
并且线程ID并不重要，所以就不深究了

<img class="half" src="/../images/unity/ECS框架学习笔记/线程-2.png"></img>



##### 调度方法

`IJobEntity.Run()`：立即在当前线程上执行，完成后再进入下一个System，并不一定是在主线程

`IJobEntity.Schedule()`：单线程调度。将job调度到一个工作线程上，但不是并行的。所有符合查询条件的实体会按照顺序在同一个线程上依次处理。线程安全不用担心数据竞争或冲突，适合不需要复杂的并行计算，或者实体数量较少时使用。

`IJobEntity.ScheduleParallel()`：并行调度。将job调度为并行执行的任务。会拆分为多个批次，并在不同的线程上处理这些批次。实体较多时可显著提高性能，但可能会引发数据竞争或冲突

>  当实体数量较多，并且每个实体的处理相对独立（没有数据竞争）时，`ScheduleParallel` 能显著提高性能
>
> 但如果任务较小或无法保证线程安全，则可以使用 `Schedule`。



##### `[BurstCompile]`属性：

优点：

- 将代码编译为高度优化的本地机器代码（如 x86 或 ARM 架构）。与标准的 C# IL 代码相比，生成的机器代码能更有效地利用 CPU，减少不必要的性能开销。
- Burst 编译器会尝试将代码自动矢量化，可以利用CPU指令集来同时处理多个数据
- Burst 编译器生成的代码与 C# 的托管环境隔离得更彻底，减少了垃圾回收的负担

缺点：

- 调试会变得更困难，因为编译后的代码不容易映射回原始 C# 代码。可以使用Burst Inspector 来分析生成的代码

- Burst 编译器不支持一些高级 C# 特性，如虚函数、多态、异常处理等

  以下为碰到的不支持的语法，有些语法编译会提示Burst不支持，但是用起来却没有问题，是因为其退回到了普通的.NET托管代码模式了

  ```C#
  System.DateTime;		// 虽然用起来没啥问题，但是在编译后unity会报错，提示不支持
  System.Environment.Tick;		// 提示找不到该方法
  System.Diagnostics.Stopwatch.GetTimestamp(); // 同上
  System.Environment.NewLine;		// 编译提示不支持
  System.Guid.NewGuid().ToByteArray();	// 编译提示不支持
      ...			// 不列了，基本上System都会不支持
  ```

  - `System.DateTime`：
    - 报错内容：`(0,0): Burst error BC1045: Struct `System.DateTime` with auto layout is not supported`
    - 本质：`BurstCompile` 不支持带有自动内存布局的结构体，例如 `System.DateTime`。这意味着 `Burst` 不能处理其内存布局，因为它可能在不同平台上表现不同。
  - `System.Guid.ToByteArray()`
    - 报错内容：`Assets\Scripts\Malevolent\DotsHelpers.cs(25,46): Burst error BC1016: The managed function System.Guid.ToByteArray(System.Guid* this) is not supported`
    - 本质：由于调用了不支持的托管方法，`Burst` 无法编译与托管代码相关的 API，比如 `System.Guid` 的方法。

> - 只用ISystem使用Burst编译
> - 使用`[BurstCompile]`后在Profiler中可以观察到`IJobEntity`
> - 可以使用Job-Burst-OpenInspector窗口查看编译错误



#### 控制执行生命周期

```C#
public partial class PlayerSpawnerSystem : SystemBase
{
	protected override void OnUpdate()
	{
		// 获取单例，如果场景中没有或者有2个以上，Unity将报错
		EntityQuery playerEntityQuery = EntityManager.CreateEntityQuery(typeof(PlayerTag));

		// 只是读取该实体，所以不用担心值类型、引用类型的问题
		PlayerSpawner playerSpawner = SystemAPI.GetSingleton<PlayerSpawner>();

		// 创建一个命令缓冲器，将任务分批次执行
		var entityCommandBuffer = SystemAPI.GetSingleton<BeginSimulationEntityCommandBufferSystem.Singleton>().CreateCommandBuffer(World.Unmanaged);

		int spawnAmount = 2;
		if (playerEntityQuery.CalculateEntityCount() < spawnAmount)
		{
            // 注释掉在常规生命周期
			// EntityManager.Instantiate(playerSpawner.playerPrefab);
            
            // 分批次的创建物体
			entityCommandBuffer.Instantiate(playerSpawner.playerPrefab);
            
			// 并不是真正的设置，而是创建了一个新的Component替换旧的
			entityCommandBuffer.SetComponent(entity, new Speed
			{
				value = DotsHelpers.GetRandomFloat(0, 2)
			});
		}
	}
}
```

<img class="half" src="/../images/unity/ECS框架学习笔记/生命周期.png"></img>



---


### Profiler

可以根据System窗口的顺序查找

<img class="half" src="/../images/unity/ECS框架学习笔记/Profiler-1.png"></img>





---

### 场景互通

#### GameObject获取Entities场景中的实体

```C#
using Unity.Entities;
using Unity.Transforms;
using UnityEngine;
using Random = UnityEngine.Random;

public class PlayerVisual : MonoBehaviour
{
	private Entity _targetEntity;

	private void LateUpdate()
	{
		if (Input.GetKeyDown(KeyCode.Space))
		{
			_targetEntity = GetRandomEntity();
		}
		
		if (_targetEntity != Entity.Null)
		{
			// 获取目标实体的坐标
			var followPosition = World.DefaultGameObjectInjectionWorld.EntityManager.GetComponentData<LocalToWorld>(_targetEntity).Position;
			transform.position = followPosition;
		}
	}

	private Entity GetRandomEntity()
	{
		// 获取Entities场景中Tags为 "PlayerTag" 的实体
		// 因为只有一个世界，所以可以直接使用Default
		EntityQuery playerTagEntityQuery = World.DefaultGameObjectInjectionWorld.EntityManager.CreateEntityQuery(typeof(PlayerTag));
		
		// 将查找到的物体临时存储到NativeArray中
		NativeArray<Entity> entityNativeArray = playerTagEntityQuery.ToEntityArray(Allocator.Temp);

		// 返回一个随机的实体
		return entityNativeArray.Length > 0 ? entityNativeArray[Random.Range(0, entityNativeArray.Length)] : Entity.Null;
	}
}
```



---

### 性能测试

使用了ECS，那当然少不了喜闻乐见的性能测试了，生成20000个Player

<img class="half" src="/../images/unity/ECS框架学习笔记/性能测试-1.png"></img>

<img class="half" src="/../images/unity/ECS框架学习笔记/性能测试-2.png"></img>

GameObject的Player生成与移动逻辑代码如下：

```C#
public class PlayerSpawnerGameObject : MonoBehaviour
{
	public GameObject playerPrefab;

	private void Start()
	{
		int spawnAmount = 20000;
		for (int i = 0; i < spawnAmount; i++)
		{
			GameObject playerGameObject = Instantiate(playerPrefab);
			var moveToPositionGameObject = playerGameObject.AddComponent<MoveToPositionGameObject>();

			moveToPositionGameObject.speed = Random.Range(2, 5);
		}
	}
}
```

```C#
public class MoveToPositionGameObject : MonoBehaviour
{
	const float TwoPi = 2f * math.PI;
	private Vector3 targetPosition;
	public float speed;

	private void Update()
	{
		Move(Time.deltaTime);
	}
	
	public void Move(float deltaTime)
	{
		var direction = (targetPosition - transform.position).normalized;
		transform.position += direction * deltaTime * speed;
		
		if (Vector3.Distance(targetPosition, transform.position) < .5f)
		{
			targetPosition = GetRandomPosition();
		}
	}

	public Vector3 GetRandomPosition(float radius = 10f, float3 center = default)
	{            
		var angle = Random.Range(0, TwoPi);
		var distance = Random.Range(0, radius);
		var x = math.cos(angle) * distance;
		var z = math.sin(angle) * distance;
		return new float3(x, 0, z) + center;
	}
}
```



---

### 总结

总得来说，搞清楚工作流程之后还是挺简单的，但以上演示是最简单的操作方式，还需要继续学习。

- 比如可以使用`[UpdateInGroup(typeof(InitializationSystemGroup), OrderLast = true)]`属性修饰System控制生命周期
- System中还有诸如`OnCreate`、`OnStartRunning`等抽象方法复写





