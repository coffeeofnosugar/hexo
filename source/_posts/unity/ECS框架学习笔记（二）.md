---
title: 【Unity】ECS框架学习笔记（二）——踩坑
date: 2024-09-15 07:11:06
tags:
  - Unity
  - ECS
---

### 属性

#### `[RequireMatchingQueriesForUpdate]`

在Update中使用 `Entities.WithAll<>()`, `Entities.WithAny<>()`, `Entities.ForEach()` 等方法时，Unity 会自动生成一个 `EntityQuery`（`IJobEntity`也会创建）。系统通过这个 `EntityQuery` 去查找符合条件的实体。

该属性的作用是确保只有在系统的 `EntityQuery` 匹配了实际的实体数据时，系统才会执行update方法。





---

### 实用接口

```C#
SystemAPI.HasComponent<ChampTag>(entity)；									//判断entitiy是否拥有某组件
var newtworkId = SystemAPI.GetComponent<GhostOwner>(entity).NetwordId;		// 直接获取entity上的组件
```







---

### 技巧

#### 存储单例

如果确定整个场景只有确定个数的实体，并且数量也不会改变，那么可以直接在`OnStartRunning`直接获取到该实体并保存

经测试确实可行

```C#
public partial class PlayerMoveSystem_______ : SystemBase
{
    private Entity playerEntity;

    protected override void OnCreate()
    {
        RequireForUpdate<PlayerTag>();
    }

    protected override void OnStartRunning()
    {
        // 获取一个
        playerEntity = SystemAPI.GetSingletonEntity<PlayerTag>();
        // 获取多个
        // foreach (var (tag, entity) in SystemAPI.Query<PlayerTag>().WithEntityAccess())
        // {
        //     playerEntity = entity;
        //     break; // 只需要第一个玩家实体
        // }
    }

    protected override void OnUpdate()
    {
        var deltaTime = SystemAPI.Time.DeltaTime;
        var moveInput = SystemAPI.GetComponent<PlayerMoveInput>(playerEntity);
        var transform = SystemAPI.GetComponentRW<LocalTransform>(playerEntity);
        var speed = SystemAPI.GetComponent<Speed>(playerEntity);

        transform.ValueRW.Position.xz += moveInput.Value * speed.Value * deltaTime;
    }
}
```

```C#
[UpdateBefore(typeof(TransformSystemGroup))]
public partial struct PlayerMoveSystem : ISystem
{
    public void OnCreate(ref SystemState state)
    {
        state.RequireForUpdate<BeginInitializationEntityCommandBufferSystem.Singleton>();
    }
    public void OnUpdate(ref SystemState state)
    {
        var deltaTime = SystemAPI.Time.DeltaTime;

        /*
        JobHandle job = 
            new PlayerMoveJob()
        {
            DeltaTime = deltaTime
        }.Schedule(state.Dependency);
        job.Complete();*/

        foreach (var (moveInput, transform, speed) in SystemAPI.Query<PlayerMoveInput, RefRW<LocalTransform>, Speed>())
        {
            transform.ValueRW.Position.xz += moveInput.Value * speed.Value * deltaTime;
        }
    }
}
```

<img class="half" src="/../images/unity/ECS框架学习笔记/存储实体.png"></img>

> 使用job与直接foreach的性能一样，这里就不贴图了



#### 监控数量

使用`EntityQuery`监控指定类型的数量

```c#
public partial class PlayerSpawnerSystem : SystemBase
{
	protected override void OnUpdate()
	{
		EntityQuery playerEntityQuery = EntityManager.CreateEntityQuery(typeof(PlayerTag));

		PlayerSpawner playerSpawner = SystemAPI.GetSingleton<PlayerSpawner>();

		var entityCommandBuffer = SystemAPI.GetSingleton<BeginSimulationEntityCommandBufferSystem.Singleton>().CreateCommandBuffer(World.Unmanaged);

		int spawnAmount = 10;
		if (playerEntityQuery.CalculateEntityCount() < spawnAmount)
		{
			var entity = entityCommandBuffer.Instantiate(playerSpawner.playerPrefab);
			
			entityCommandBuffer.SetComponent(entity, new Speed
			{
				value = DotsHelpers.GetRandomFloat(2, 5)
			});
		}
	}
}
```

或者

```C#
public partial struct ClientRequestGameEntrySystem : ISystem
{
    private EntityQuery _pendingNetworkIdQuery;

    public void OnCreate(ref SystemState state)
    {
        // 虽然是在OnCreate中创建的Query，但是并没有销毁掉，所以还是会一直更新里面的实体
        var builder = new EntityQueryBuilder(Allocator.Temp).WithAll<NetworkId>().WithNone<NetworkStreamInGame>();
        _pendingNetworkIdQuery = state.GetEntityQuery(builder);
        state.RequireForUpdate(_pendingNetworkIdQuery);
    }
    public void OnUpdate(ref SystemState state)
    {
        var pendingNetworkIds = _pendingNetworkIdQuery.ToEntityArray(Allocator.Temp);
    }
}
```

`ISystem`的用法，需要使用`.Dispose()`手动释放资源

```C#
var query = SystemAPI.QueryBuilder().WithAll<NewEnemyTag>().Build();
```

#### 移除组件

v1.2.4貌似添加和删除组件都只能使用缓冲器

确认之后不会再使用的组件可以使用缓冲器移除

```C#
var ecb = SystemAPI.GetSingleton<EndInitializationEntityCommandBufferSystem.Singleton>().CreateCommandBuffer(state.WorldUnmanaged);		// 延迟到这一帧初始组结束时移除
foreach (var (_, entity) in SystemAPI.Query<NewEnemyTag>().WithEntityAccess())
{
    ecb.RemoveComponent<NewEnemyTag>(entity);
}
```

```C#
var ecb = new EntityCommandBuffer(Allocator.Temp);			// 立即移除
foreach (var (_, entity) in SystemAPI.Query<NewEnemyTag>().WithEntityAccess())
{
    ecb.RemoveComponent<NewEnemyTag>(entity);
}
ecb.Playback(state.EntityManager);
```







---

### `BlobArray<T>`

特点：

- 允许存储大量数据，并且只读
- 存储在一块连续的内存区域，访问速度快，缓存友好
- 由于是只读的，所以可以在多个线程中安全地共享和访问

使用方法：

1. 定义`BlobArray`和`BlobAsset`

   ```C#
   public struct SpawnEnemyPoint : IComponentData
   {
       public BlobAssetReference<SpawnEnemyPointBlob> Value;
   }
   
   public struct SpawnEnemyPointBlob
   {
       public BlobArray<float3> Value;
   }
   ```

2. 将`SpawnEnemyPoint`烘焙到任意实体上

3. 使用`BlobBuilder`赋值

   ```C#
   // 初始化一个临时用的builder
   using (BlobBuilder builder = new BlobBuilder(Allocator.Temp))
   {
       // 确定需要存储的Blob结构体数据类型
       ref SpawnEnemyPointBlob pointBlob = ref builder.ConstructRoot<SpawnEnemyPointBlob>();
       // 分配大小空间
       BlobBuilderArray<float3> arrayBuilder = builder.Allocate(ref pointBlob.Value, 10);
       // 填充数据
       for (int i = 0; i < 10; i++)
       {
           arrayBuilder[i] = new float3{i, 0f, 0f};
       }
       // 创建Blob的引用（类似于指针？）
       BlobAssetReference<SpawnEnemyPointBlob> blobAsset = builder.CreateBlobAssetReference<SpawnEnemyPointBlob>(Allocator.Persistent);
       // 将创建的引用赋值给gameEntity的组件上，供其使用
       ecb.SetComponent(gameEntity, new SpawnEnemyPoint(){Value = blobAsset});
   }
   ```

4. 使用方法与列表一样

   ```C#
   private readonly RefRO<SpawnEnemyPoint> _spawnEnemyPoint;
   var position = _spawnEnemyPoint.ValueRO.Value.Value.Value[0];
   ```

   


> 为什么不直接将`BlobArray`当做`IComponentData`挂载到实体上？
>
> 1. 将`BlobArray`直接放在实体上，每个实体都会有独立的`BlobArray`副本，大大增加了内存使用
>    `BlobAssetReference` 存储的是指向连续内存块的指针
>    多个实体可以共享一个`BlobArray`，而不需要为每个实体分配内存
> 2. `IComponentData`是可更改的，每次修改组件都可能会导致内存重新分配和复制，对于不可变数据来说不必要



---

### `System`报错

#### `InvalidOperationException: The previously scheduled 'IJobEntity' writes to the ComponentTypeHandle<Unity.Collections.NativeText.ReadOnly>`

```C#
InvalidOperationException: The previously scheduled job <AJob> writes to the ComponentTypeHandle<Unity.Collections.NativeText.ReadOnly> <AJob>.<Value>.
You are trying to schedule a new job <BJob>, which reads from the same ComponentTypeHandle<Unity.Collections.NativeText.ReadOnly> (via <BJob>.<Value>).
To guarantee safety, you must include PlayerMoveSystem:PlayerMoveJob as a dependency of the newly scheduled job.
```

- 两个任务共同访问了同一个`IComponentData`

##### 原因

两个`System.IJobEntity`的`IAspect`中以**读写**的方式定义了同一个实体的组件数据

如`生成敌人系统`和`敌人移动系统`，在Systems窗口中可以看到两个系统的执行先后

> 根本原因：
>
> - 没有定义系统之间执行顺序
> - `Run()`执行完后再才进入下一个system，并且在执行期间会保护数据，其他系统只能读取无法修改`Run()`所访问的**读写**组件



##### 错误代码

生成敌人**错误**代码：

```c#
public partial struct SpawnEnemySystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        new AJob().Run();	// 立即在当前线程上执行，完成后再进入下一个System，期间的数据其他system无法修改其访问的组件
    }
}
    
private partial struct AJob : IJobEntity
{
    private void Execute(TestAspect aspect) { }
}
```

```c#
public readonly partial struct TestAspect : IAspect
{
    readonly RefRW<TargetPosition> targetPosition;
}
```

移动系统**错误**代码：

```C#
public partial struct EnemyMoveSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        new BJob().Schedule();		// 调度任务到其他线程访问
    }
}

public partial struct BJob : IJobEntity
{
    private void Execute(EnemyMoveAspect enemy) { }
}
```

```C#
public readonly partial struct EnemyMoveAspect : IAspect
{
    readonly RefRO<EnemyTag> enemyTag;
    readonly RefRW<TargetPosition> targetPosition;
}
```

> 从上面的代码可以看出，仅仅只是引用就会报错
>
> 这里生成和移动敌人例子可能不太合理，但只要理解到两个系统的`IAspect`以**读写**的方法定义了同一个的实体的同一个组件就OK了
>
> <font color="DarkGray">注意：为了节约空间简化了不少代码</font>



##### 解决方法

方法一：

使用`UpdateAfer`属性定义执行顺序

```C#
[UpdateAfter(typeof(SpawnEnemySystem))]
public partial struct EnemyMoveSystem : ISystem
```

这样，在成功生成敌人后，在执行移动系统，移动系统就不会在敌人还在生成的时候就修改其组件

方法二：

将选择其中Entity较少的任务设置依赖项，并等待其编译完成

```C#
public partial struct EnemyMoveSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        JobHandle job = new BJob().Schedule(state.Dependency);		// 设置依赖项
        job.Complete();		// 主线程被阻塞，直到该任务完成
    }
}
```

方法三：

使用`Query`获取`Aspect`

```C#
public partial struct EnemyMoveSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        foreach(var aspect in SystemAPI.Quert<RefRW<MoveAspect>>.WithEntityAccess())
        {
            ...
        }
    }
}
```





#### `InvalidOperationException: 'EntityCommandBuffer' is not declared [ReadOnly] in a IJobParallelFor job. The container does not support parallel writing. Please use a more suitable container type.`

##### 原因

该容器不支持并行写入



##### 错误代码

```c#
public partial struct EnemyMoveSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var ecb = SystemAPI.GetSingleton<EndSimulationEntityCommandBufferSystem.Singleton>().CreateCommandBuffer(state.WorldUnmanaged);

        new EnemyMoveJob
        {
            ECB = ecb
        }.ScheduleParallel();
    }

    public partial struct EnemyMoveJob : IJobEntity
    {
        public EntityCommandBuffer ECB;

        private void Execute(EnemyMoveAspect enemy)
        {
			ECB.RemoveComponent<EnemyTag>(enemy.Entity);
        }
    }
}
```



##### 解决方法

修改类型成[可并行写入的缓冲器容器](https://docs.unity3d.com/Packages/com.unity.entities@1.2/manual/systems-entity-command-buffer-use.html)

```C#
var ecb = SystemAPI.GetSingleton<EndSimulationEntityCommandBufferSystem.Singleton>().CreateCommandBuffer(state.WorldUnmanaged).AsParallelWriter();
```

```c#
private void Execute(EnemyMoveAspect enemy, [ChunkIndexInQuery]int sortKey)	// 并不是普通的int类型，需要指定类型
{
    ECB.RemoveComponent<EnemyTag>(sortKey, enemy.Entity);
}
```

[使用方法](https://docs.unity3d.com/Packages/com.unity.entities@1.2/manual/systems-entity-command-buffer-playback.html#deterministic-playback-in-parallel-jobs)：需要指定执行的顺序，如果没有特殊的顺序需要考虑，可以使用`ChunkIndexInQuery`

> `ChunkIndexInQuery`：
>
> 在ECS中，`EntityQuery` 会返回多个 "chunk"（即实体的内存块），而每个 "chunk" 存储一组符合查询条件的实体`ChunkIndexInQuery` 就是这些 `chunk` 在整个查询中的唯一索引值。
>
> 每个 `chunk` 在查询的范围内都有一个唯一的索引值，避免多个 `chunk` 之间产生混淆。
>
> 即使调度方式发生变化（例如工作在多个线程之间并行执行），这个索引值也保持不变，保证了在不同的调度执行顺序下，`ChunkIndexInQuery` 始终一致。
>
> 因为索引值是确定且稳定的，所以在使用 `EntityCommandBuffer`（ECB）时，可以保证对实体的操作是可预测和一致的（例如，记录、重放命令时不受并行或调度的影响）。



