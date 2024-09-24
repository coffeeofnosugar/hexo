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
Entity entity = SystemAPI.GetSingletonEntity<PlayerTag>();						 // 获取实体
bool has = SystemAPI.HasComponent<ChampTag>(entity)；							// 判断entitiy是否拥有某组件
GhostOwner newtworkId = SystemAPI.GetComponent<GhostOwner>(entity).NetwordId;	// 直接获取entity上的组件
bool entityExists = EntityManager.Exists(entity);								// 判断实体是否存在有效
bool has = SystemAPI.HasSingleton<GamePlayingTag>()							// 判断整个场景中是否有组件，几个无所谓
```







---

### 技巧

#### 单例

##### 保存单例的引用

如果确定整个场景只有确定个数的实体，并且数量也不会改变，那么可以直接在`OnStartRunning`直接获取到该实体并保存

<font color='red'>该方法只适合SystemBase。如果想在Isystem的OnCreate中保存单例，后续使用该组件的时候会报错，提示引用丢失</font>

```C#
// 实验组——存储单例
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
// 对照组——直接查找对象
[UpdateBefore(typeof(TransformSystemGroup))]
public partial struct PlayerMoveSystem : ISystem
{
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

以上两种方式的性能测试结果：

<img class="half" src="/../images/unity/ECS框架学习笔记/存储单例.png"></img>

##### 设置单例属性

在确定一个组件为单例时，可以使用`SystemAPI.SetSingleton(IComponentData)`保存该组件的值

> - 该组件必须没有实现`IEnableableComponent`或`EntityQuery.SetSingleton{T}`
> - 无法在`Entities.ForEach`、`IJobEntity`、`Utility methods`或`Aspects`中使用

```c#
var gamePropertyEntity = SystemAPI.GetSingletonEntity<GameStartProperties>();
var teamPlayerCounter = SystemAPI.GetComponent<TeamPlayerCounter>(gamePropertyEntity);
SystemAPI.SetSingleton(teamPlayerCounter);		// 设置该组件的值
```



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
ecb.Playback(state.EntityManager);			// 手动创建的ecb需要手动触发
```

#### 使创建的方法能使用SystemAPI接口

```C#
public void OnUpdate(ref SystemState state)
{
    SpawnOnEachLane(ref state);
}
private void SpawnOnEachLane(ref SystemState state)		// 如果没有传入state，就无法使用SystemAPI的接口
{
	var ecbSingleton = SystemAPI.GetSingleton<BeginSimulationEntityCommandBufferSystem.Singleton>();
}
```

#### 一个组件烘焙多次

一个实体上只能拥有一个同名的组件，如果一个组件需要挂载多次，可以使用`CreateAdditionalEntity`创建一个额外的实体

```C#
public Vector3[] TopLanePath;
public Vector3[] MidLanePath;
public Vector3[] BotLanePath;

public override void Bake(MinionPathAuthoring authoring)
{
    var entity = GetEntity(TransformUsageFlags.None);		// 创建本身
    // 添加
    var topLane = CreateAdditionalEntity(TransformUsageFlags.None, false, "TopLane");
    var midLane = CreateAdditionalEntity(TransformUsageFlags.None, false, "MidLane");
    var botLane = CreateAdditionalEntity(TransformUsageFlags.None, false, "BotLane");
    var topLanePath = AddBuffer<MinionPathPosition>(topLane);
    var midLanePath = AddBuffer<MinionPathPosition>(midLane);
    var botLanePath = AddBuffer<MinionPathPosition>(botLane);
}
```

#### 灵活使用关键字`WithAny`捕获

`WithAny`只要有一个符合就捕获

```c#
// 捕获拥有碰撞物理，且有队伍的实体					// 既可以是英雄，也可以是小兵
SystemAPI.Query<RefRW<PhysicsMass>, MobaTeam>().WithAny<NewChampTag, NewMinionTag>()；
```









---

### 关于Tick和`IsFirstTimeFullyPredictingTick`

参考[Full vs. Partial Ticks ](https://discussions.unity.com/t/full-vs-partial-ticks/941512)

- <font color='red'>**Tick是固定一秒60次，并不是update执行的次数**</font>。由于服务器没反应过来，服务器update的次数一般都会比Tick次数少，客户端反应比较快一半会比60大。

  - 服务端会将数据以Tick的频率发送给客户端，而客户端会平滑的设置其数值，有如下两种情景

    - 数值：服务端告诉客户端第20Tick`Value = 10`，那么客户端在19Tick（假设`Value=0`）与20Tick之间会**多次执行**update，让Value从0平滑的到达10。假如客户端一个Tick可以运行10次，那么value第一次update为0，第二次update为1，第三次update为3....直到完整的到达第20Tick，Value就等于10了。

    - 事件：服务端告诉客户端第20Tick的时候创建一个小兵，那么在19Tick与20Tick之间，每次update都会创建一个小兵

      这时就需要用到`IsFirstTimeFullyPredictingTick`了，在19到20Tick之间update`IsFirstTimeFullyPredictingTick`返回false；当你真正达到20Tick，`IsFirstTimeFullyPredictingTick`返回True，表示这是第一次完整的预测Tick

    假设有代码如下：

    ```C#
    // [UpdateInGroup(typeof(PredictedSimulationSystemGroup))]	system在模拟组中
    
    var networkTime = SystemAPI.GetSingleton<NetworkTime>();
    if (networkTime.IsFirstTimeFullyPredictingTick)
    {
        ecb.生成小兵();				// 只有在20Tick的时候才会执行
    }
    Value = 10;			// 在18到20Tick之间，客户端每次update都将让Value更接近10
    					// 虽然这里写的是直接赋值，但客户端并不会生硬的将Value设置为10
    ```

    <img class="half" src="/../images/unity/ECS框架学习笔记/IsFirstTimeFullyPredictingTick用法.png"></img>

  {% grouppicture 2-2 %}

  <img class="half" src="/../images/unity/ECS框架学习笔记/服务端Tick与Update.png"></img>

  <img class="half" src="/../images/unity/ECS框架学习笔记/客户端Tick与Update.png"></img>

  {% endgrouppicture %}

- 服务端与客户端的Tick并不同步。这应该就是延迟的由来？

  {% grouppicture 2-2 %}

  <img class="half" src="/../images/unity/ECS框架学习笔记/服务端Tick.png"></img>

  <img class="half" src="/../images/unity/ECS框架学习笔记/客户端Tick.png"></img>

  {% endgrouppicture %}

测试代码：

```c#
public partial struct TestSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var isServer = state.WorldUnmanaged.IsServer();
        if (isServer)
        {
        	var networkTime = SystemAPI.GetSingleton<NetworkTime>();
            Debug.Log($"Server: Tick: {networkTime.ServerTick}, ElapsedTime: {SystemAPI.Time.ElapsedTime}");
            Debug.Log("Server: Update time");
        }
        else
        {
        	var networkTime = SystemAPI.GetSingleton<NetworkTime>();
            Debug.Log($"Client: Tick: {networkTime.ServerTick}, ElapsedTime: {SystemAPI.Time.ElapsedTime}");
            Debug.Log("Client: Update time");
        }
    }
}
```





---

### GameObject与Entities世界交互

#### GameObject => Entities

系统：

```C#
// 判断Default World中 PlayerMoveSystem 系统是否存在
ClientStartGameSystem startGameSystem = World.DefaultGameObjectInjectionWorld.GetExistingSystemManaged<ClientStartGameSystem>();
// 直接使用系统中的公开属性
startGameSystem.OnUpdatePlayersRemainingToStart -= UpdatePlayerRemainingText;
```

实体：

```C#
// 创建实体
Entity entity = World.DefaultGameObjectInjectionWorld.EntityManager.CreateEntity();
// 添加组件
World.DefaultGameObjectInjectionWorld.EntityManager.AddComponentData(teamRequestEntity, new ClientTeamSelect(){ Value = team });
```

```C#
// 捕获EntityQuery
EntityQuery playerTagEntityQuery = World.DefaultGameObjectInjectionWorld.EntityManager
    .CreateEntityQuery(typeof(PlayerTag));	// 只读
EntityQuery networkDriverQuery = World.DefaultGameObjectInjectionWorld.EntityManager
    .CreateEntityQuery(ComponentType.ReadWrite<NetworkStreamDriver>());	// 读写
// 保存捕获到的Entity
NativeArray<Entity> entityNativeArray = networkDriverQuery.ToEntityArray(Allocator.Temp);
// 修改组件
networkDriverQuery.GetSingletonRW<NetworkStreamDriver>().ValueRW.Listen(serverEndpoint);
```



> 如果使用了NetCode包，在创建Client World时，需要将Default World设置为Cilient World
>
> ```C#
> // 创建Client World
> var clientWorld = ClientServerBootstrap.CreateClientWorld("Coffee Client World");
> // 将Default World 设置为 Cilient World
> World.DefaultGameObjectInjectionWorld = clientWorld;
> ```



#### Entities => GameObject

方法一：单例，比较简单，就不说了

方法二：创建GameObject时保存对其的引用，方法如下

```C#
public class HealthBarUIReference : ICleanupComponentData		// 注意这里使用的是class而不是结构体
{
    public GameObject Value;
}
// 创建GameObject
var newHealthBar = Object.Instantiate(healthBarPrefab, spawnPosition, quaternion.identity);
// 将GameObject的引用保存在组件上
ecb.AddComponent(entity, new HealthBarUIReference() { Value = newHealthBar });
// 获取该组件并使用
foreach(var obj in SystemAPI.Query<HealthBarUIReference>())
{
    obj.Value.transform = new Vector3(1f, 0f, 0f);		// 改变位置坐标
    Slider slider = obj.GetComponentInChildren<Slider>(); // 获取子物体的UI。能获取到组件，那么就很灵活了
}
```

> 由于烘焙的时候只能挂载预制体，所以entities无法直接引用到GameObject中的物体







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



---

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



---

#### `'MultiplayerDOTS.NpcAttackSystem' creates a Lookup object (e.g. ComponentLookup) during OnUpdate. Please create this object in OnCreate instead and use type `_MyLookup.Update(ref systemState);` in OnUpdate to keep it up to date instead. This is significantly faster.`

##### 原因

在使用了错误的API

##### 错误代码

```C#
state.Dependency = new NpcAttackJob()
{
    TransformLookup = state.GetComponentLookup<LocalTransform>(true),
}.ScheduleParallel(state.Dependency);
```

##### 解决方法

```C#
state.Dependency = new NpcAttackJob()
{
    TransformLookup = SystemAPI.GetComponentLookup<LocalTransform>(true),
}.ScheduleParallel(state.Dependency);
```

