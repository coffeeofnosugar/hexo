---
title: 【Unity】ECS框架学习笔记（三）——多人联网
date: 2024-09-20 12:036:06
tags:
  - Unity
  - ECS
---

### 夺回生成世界的控制权

在下载NetCode包体之后，启动游戏时Entities会生成ClientWorld和ServerWorld两个世界。
但玩家进入游戏的流程是：先进入主菜单，再进入游戏。在主菜单的时候不用生成ServerWorld，所以我们需要拿到控制权。

将`Overide Automatic Netcode Bootstrap`组件挂载到场景中的任意物体上并选择`Disable Automatic Bootstrap`
因为我们要控制所有场景的世界生成，所以所有场景都需要挂载

<img class="half" src="/../images/unity/ECS框架学习笔记/Bootstrapper.png"></img>

挂载之后，启动场景时只会生成`Default World`。
然后我们从主菜单进入游戏的时候删除掉`Default World`，生成`Client World`和`Server World`就OK了。



---

### 删除默认世界

进入游戏场景时删除`Default World`，正好在切换场景的时候删除掉所有内容

```C#
// 遍历所有Entity并删除
foreach (var world in World.All)
{
    if (world.Flags == WorldFlags.Game)
    {
        world.Dispose();
        break;
    }
}
// 上面只能删除Entity，并不会删除GameObject的，所以需要使用Single
SceneManager.LoadScene(1, LoadSceneMode.Single);
```

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/ECS框架学习笔记/DefaultWorld.png"></img>

<img class="half" src="/../images/unity/ECS框架学习笔记/Client&ServerWorld.png"></img>

{% endgrouppicture %}



---

### 创建服务端和客户端世界

#### 服务端：

```c#
private void StartServer()
{
    var serverWorld = ClientServerBootstrap.CreateServerWorld("Coffee Server World");	// 创建服务端世界

    // 使服务器监听7979端口
    var serverEndpoint = NetworkEndpoint.AnyIpv4.WithPort(7979);
    {
        using var networkDriverQuery = serverWorld.EntityManager.CreateEntityQuery(ComponentType.ReadWrite<NetworkStreamDriver>());
        networkDriverQuery.GetSingletonRW<NetworkStreamDriver>().ValueRW.Listen(serverEndpoint);
    }
}
```

> 获取的`NetworkStreamDriver`组件为NetCode的特殊`IComponentData`

#### 客户端：

```C#
public enum TeamType : byte
{
    None = 0,
    Blue = 1,
    Red = 2,
    AutoAssign = byte.MaxValue
}
public struct ClientTeamSelect : IComponentData
{
    public TeamType Value;
}
```

```C#
private void StartClient()
{
    var clientWorld = ClientServerBootstrap.CreateClientWorld("Coffee Client World");	// 创建客户端世界

    var connectionEndpoint = NetworkEndpoint.Parse("127.0.0.1", 7979);		// 将用户输入转换成网络地址
    {
        // 根据端口连接服务端
        using var networkDriverQuery = clientWorld.EntityManager.CreateEntityQuery(ComponentType.ReadWrite<NetworkStreamDriver>());
        networkDriverQuery.GetSingletonRW<NetworkStreamDriver>().ValueRW.Connect(clientWorld.EntityManager, connectionEndpoint);
    }

    // 将对Default World世界的操作同步到Client World，以免每次操作都要使用Client的API
    World.DefaultGameObjectInjectionWorld = clientWorld;

    var team = _teamDropdown.value switch		// 设置传递给Entities的信息
    {
        0 => TeamType.AutoAssign,
        1 => TeamType.Blue,
        2 => TeamType.Red,
        _ => TeamType.None
    };
    
	// 将用户在GameObject中选择的队伍传递到Entities中，！！！注意：这里并没有向服务端发送请求
    var teamRequestEntity = clientWorld.EntityManager.CreateEntity();
    clientWorld.EntityManager.AddComponentData(teamRequestEntity, new ClientTeamSelect()
    {
        Value = team
    });
}
```

> - <font color="red">注意</font>：`World.DefaultGameObjectInjectionWorld = clientWorld;`这个很重要，可以直接将对Default World世界的操作同步到Client World，以免每次操作都要使用Client的API。我们已经删除掉默认世界了，所以不会有重复的多余操作
> - 需要注意的是，这里并没有向服务器发送信息，只是将GameObject的信息传递到Entities的客户端中



---

### 客户端向服务器发送进入游戏请求

```c#
// 只在客户端运行
[WorldSystemFilter(WorldSystemFilterFlags.ClientSimulation | WorldSystemFilterFlags.ThinClientSimulation)]   
public partial struct ClientRequestGameEntrySystem : ISystem
{
    private EntityQuery _pendingNetworkIdQuery;

    public void OnCreate(ref SystemState state)
    {
        // 捕获有`NetworkId`且没有`NetworkStreamInGame`的实体
        var builder = new EntityQueryBuilder(Allocator.Temp).WithAll<NetworkId>().WithNone<NetworkStreamInGame>();
        _pendingNetworkIdQuery = state.GetEntityQuery(builder);
        state.RequireForUpdate(_pendingNetworkIdQuery);
        state.RequireForUpdate<ClientTeamSelect>();        // 获取在登入界面创建的组件
    }

    public void OnUpdate(ref SystemState state)
    {
        // 获取在登入界面创建的组件
        var requestedTeam = SystemAPI.GetSingleton<ClientTeamSelect>().Value;

        var ecb = new EntityCommandBuffer(Allocator.Temp);
        var pendingNetworkIds = _pendingNetworkIdQuery.ToEntityArray(Allocator.Temp);

        foreach (Entity pendingNetworkId in pendingNetworkIds)// 肯定是只有一个的，所以也使用pendingNetworkIds[0]
        {
            ecb.AddComponent<NetworkStreamInGame>(pendingNetworkId); // 将物体标记为进入游戏，该组件是一个Tag
            
            // 向服务器发送请求，这里才是真正向服务器发送请求
            var requestTeamEntity = ecb.CreateEntity();
            ecb.AddComponent(requestTeamEntity, new MobaTeamRequest() { Value = requestedTeam });
            ecb.AddComponent(requestTeamEntity, new SendRpcCommandRequest() { TargetConnection = pendingNetworkId });
        }

        ecb.Playback(state.EntityManager);		// 等待缓冲器完成所有任务
    }
}
```

> 只在客户端运行：
>
> `[WorldSystemFilter(WorldSystemFilterFlags.ClientSimulation | WorldSystemFilterFlags.ThinClientSimulation)] `

> <font color="red">发送数据包：</font>
>
> ```C#
> var requestTeamEntity = ecb.CreateEntity();
> ecb.AddComponent(requestTeamEntity, new MobaTeamRequest() { Value = requestedTeam });
> ecb.AddComponent(requestTeamEntity, new SendRpcCommandRequest() { TargetConnection = pendingNetworkId });
> ```
>
> - `MobaTeamRequest`为信息内容，虽然是使用`AddComponent`添加，但其实是`IRpcCommand`，而不是`IComponentData`
>
>   ```C#
>   public struct MobaTeamRequest : IRpcCommand
>   {
>       public TeamType Value;
>   }
>   ```
>
> - `SendRpcCommandRequest`为NetCode特殊组件
>
>   - 将Entity传递过去，即上图的`NetworkConnectiuon`
>   - 与服务器的`ReceiveRpcCommandRequest`对应
>
>   ```C#
>   namespace Unity.NetCode
>   {
>     public struct SendRpcCommandRequest : IComponentData, IQueryTypeParameter
>     {
>       public Entity TargetConnection;
>     }
>   }
>   ```



---

### 服务端接收玩家进入请求创建网络连接并创建幽灵系统的Entity

如果这里看不懂的话可以先看下面的RPC和Ghost

```C#
[WorldSystemFilter(WorldSystemFilterFlags.ServerSimulation)]      // 只在服务端运行
public partial struct ServerProcessGameEntryRequestSystem : ISystem
{
    public void OnCreate(ref SystemState state)
    {
        state.RequireForUpdate<MobaPrefabs>();
        var builder = new EntityQueryBuilder(Allocator.Temp).WithAll<MobaTeamRequest, ReceiveRpcCommandRequest>();
        state.RequireForUpdate(state.GetEntityQuery(builder));  // 获取到信息包才执行update
    }

    public void OnDestroy(ref SystemState state) { }

    public void OnUpdate(ref SystemState state)
    {
        var ecb = new EntityCommandBuffer(Allocator.Temp);
        var championPrefab = SystemAPI.GetSingleton<MobaPrefabs>().Champion;    // 获取角色预制体

        foreach (var (teamRequest, requestSource, requestEntity) 
                 in SystemAPI.Query<MobaTeamRequest, ReceiveRpcCommandRequest>().WithEntityAccess())
        {
            ecb.DestroyEntity(requestEntity);   // 客户端发送的请求包，但这里需要手动销毁。
            // requestSource.SourceConnection为客户端存放在服务端上的连接器，每个客户端就会存放一个
            ecb.AddComponent<NetworkStreamInGame>(requestSource.SourceConnection);

            // 数据处理
            var requestedTeamType = teamRequest.Value;

            if (requestedTeamType == TeamType.AutoAssign)
            {
                requestedTeamType = TeamType.Blue;
            }

            float3 spawnPosition = new float3(0, 1, 0);

            switch (requestedTeamType)
            {
                case TeamType.Blue:
                    spawnPosition = new float3(-50f, 1f, -50f);
                    break;
                case TeamType.Red:
                    spawnPosition = new float3(50f, 1f, -50f);
                    break;
                default:
                    continue;
            }
			     // 获取客户端ID
            var clientId = SystemAPI.GetComponent<NetworkId>(requestSource.SourceConnection).Value;

            // Debug.Log($"{clientId}   {requestedTeamType.ToString()}");

            var newChamp = ecb.Instantiate(championPrefab);         // 实例化角色
            ecb.SetName(newChamp, "Champion");      // 方便测试，设置名称
            var newTransform = LocalTransform.FromPosition(spawnPosition);
            ecb.SetComponent(newChamp, newTransform);
            // NetworkId是幽灵数据，即完全由服务端控制，设置该数值后clientId客户端对应的Entity的GhostOwnerIsLocal将被标记为true，GhostOwnerIsLocal同样也只能被服务端控制
            ecb.SetComponent(newChamp, new GhostOwner() { NetworkId = clientId });
            ecb.SetComponent(newChamp, new MobaTeam() { Value = requestedTeamType });   // 设置队伍

            // 当玩家断线重连时，会摧毁旧的Entity，并创建新的Entity
            ecb.AppendToBuffer(requestSource.SourceConnection, new LinkedEntityGroup(){ Value = newChamp }); 
        }

        ecb.Playback(state.EntityManager);
    }
}
```

> 这里我们可以查看到数据包长啥样

<img class="half" src="/../images/unity/ECS框架学习笔记/ReceiveRpcCommandRequest.png"></img>

> <font color="red">接受数据包：</font>
>
> ```C#
> foreach (var (teamRequest, requestSource, requestEntity) 
>          in SystemAPI.Query<MobaTeamRequest, ReceiveRpcCommandRequest>().WithEntityAccess())
> {
>     ecb.DestroyEntity(requestEntity);   // 客户端发送的请求包，但这里需要手动销毁。是同一个实体？
>     // requestSource.SourceConnection为客户端存放在服务端上的连接器，每个客户端就会存放一个
>     ecb.AddComponent<NetworkStreamInGame>(requestSource.SourceConnection);
>     // ...
>     // 处理数据
>     // ...
> }
> ```

> <font color="red">创建角色：</font>
>
> ```C#
> var newChamp = ecb.Instantiate(championPrefab);         // 实例化角色
> ecb.SetComponent(newChamp, new GhostOwner() { NetworkId = clientId });      // 设置该实例化角色控制的客户端ID
> // 当玩家断线重连时，系统将摧毁旧的服务端Entities，并创建新的服务端Entities
> ecb.AppendToBuffer(requestSource.SourceConnection, new LinkedEntityGroup(){ Value = newChamp });
> // ...
> // 其他设置，如position、队伍、名称等，设置名称后可以直接在`Hierarchy`窗口看到
> // ...
> ```
>
> - `GhostOwner`：将实体的控制权交给clientId客户端
>
>   ```C#
>   namespace Unity.NetCode
>   {
>   	[DontSupportPrefabOverrides]
>       [GhostComponent(SendDataForChildEntity = true)]
>       public struct GhostOwner : IComponentData
>       {
>           [GhostField] public int NetworkId;
>       }
>   }
>   ```
>   
> - 将实例化保存在`LinkedEntityGroup`中，是为了统一管理该客户端在服务端的一切事物
>
>   - 如果该客户端退出游戏或断线，就摧毁掉该一切与它有关的事物
>   - 如果重连，就重新创建列表的物体（感觉应该可以控制哪些是要生成的，哪些是不需要的？）
>
>
> <img class="half" src="/../images/unity/ECS框架学习笔记/服务端.png"></img>



---

### RPC小结

> <font color='red'>**在学习的前先搞清楚一个问题，客户端和服务端连接的方式就只是靠`NetworkConnection`，Ghost系统也只不过是建立在`NetworkConnection`上面封装好的工具而已，最终都是需要通过`NetworkConnection`在服务端和客户端传递信息。**</font>

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/ECS框架学习笔记/网络连接-客户端.png"></img>

<img class="half" src="/../images/unity/ECS框架学习笔记/网络连接-服务端.png"></img>

{% endgrouppicture %}

#### 发送数据模版：

```C#
// 代可能编译都不通过，但只是想简单的告诉你发送RPC的方法就是：
// 创建一个实体，并在其上面添加实现`IRpcCommand`接口的数据组件，和`SendRpcCommandRequest`的特殊组件就OK了
// 其他的系统会自动帮你完成
public struct LoadLevelRPC : IRpcCommand
{
    public int LevelIndex;
}
private void LoadNewLevel(int levelIndex)
{
    var rpcEntity = EntityManager.CreateEntity(typeof(LoadLevelRPC), typeof(SendRpcCommandRequest));
    EntityManager.SetComponentData(rpcEntity, new LoadLevelRpc()
    {
        LevelIndex = levelIndex
    });
}
```

这里的`SendRpcCommandRequest`没有指明对象

- 如果这是客户端发送的数据包，那么还是只会发送给服务端
- 如果这是服务端发送的数据包，那么将发送给所有客户端

#### 接受数据模版

```C#
foreach (var (levelToLoad, rpcEntity) in 
         SystemAPI.Query<LoadLevelRPC>().WithAll<ReceiveRpcCommandRequest>().WithEntityAccess())
{
    ecb.DestroyEntity(rpcEntity);			// 删除数据包
    LoadLevel(levelToLoad.LevelIndex);		// 数据处理
}
```

最重要的一点是在捕获到数据包后<font color="red">**一定要删除**</font>掉该实体。要不然这个数据一直存在，服务端就以为是客户端在不停的发送数据。

#### 流程梳理

传递的枚举TeamType数据一共有三个组件，別搞混了

- 保存在Client World和Server World的`ClientTeamSelect`、`MobaTeam`两个都是`IcompoentData`，是普通组件
  - `ClientTeamSelect`不会挂载到任何实例化对象上（也就是说不会挂载在Ghost上）。他会就这样永远孤独的漂浮在Client World中，如果想删除它也可以。
  - `MobaTeam`中数据使用`[GhostField]`修饰了，所以客户端会给对应的Ghost上添加`MobaTeam`组件，并且同步该数据。
  - 所以我们没有使用`ClientTeamSelect`来当做客户端的队伍，要不然我们还需要额外的精力去同步。
- `MobaTeamRequestRPC`是`IRpcCommand`通信用的，可以看做的临时中转站

<img class="half" src="/../images/unity/ECS框架学习笔记/数据传递流程.png"></img>

1. Client World创建了一个数据包
2. NetCode捕获到到该数据包后删除掉该数据包，并同时在Server World还原这个数据包（只将`SendRpcCommandRequest`改为了`ReceiveRpcCommandRequest`，其他数据完全一样）。这一步骤是NetCode完全自动化完成的
3. 程序员在Server World手动捕获到系统还原的这个数据包，就成功获取到数据了

> 关于这两个数据包到底是不是同一个Entity的问题：
> 直接使用代码获取到这两个Entity的`Index`、`Version`、`HashCode`就知道了
>
> 客户端：
>
> ```c#
> public void OnUpdate(ref SystemState state)
> {
>     Entity requestTeamEntity = Entity.Null;
>     // 输出刚创建时的对象信息，以防狸猫换太子
>     Debug.Log($"Send 1 : {requestTeamEntity == Entity.Null} Index: {requestTeamEntity.Index} Version: {requestTeamEntity.Version} HashCode: {requestTeamEntity.GetHashCode()}");
>     var ecb = new EntityCommandBuffer(Allocator.Temp);
>     foreach (Entity pendingNetworkId in pendingNetworkIds)
>     {
>         requestTeamEntity = ecb.CreateEntity();
>         ecb.AddComponent(requestTeamEntity, new MobaTeamRequest() { Value = requestedTeam });
>         ecb.AddComponent(requestTeamEntity, new SendRpcCommandRequest() { TargetConnection = pendingNetworkId });
>     }
> 
>     ecb.Playback(state.EntityManager);
>     Debug.Log($"Send 1 : {requestTeamEntity == Entity.Null} Index: {requestTeamEntity.Index} Version: {requestTeamEntity.Version} HashCode: {requestTeamEntity.GetHashCode()}");
> }
> ```
>
> > <font color="DarkGray">（不重要，可以跳过不看）代码为什么写成这样，要输出次：为了确认Entity是在缓存器执行完之后的信息，所以将其放在了最后面。然后又因为`requestTeamEntity`是定义在foreach中的，所以得现在最上面创建一个空的Entity，这样才能在`.Playback()`后面使用该Entity，要不然编译都不通过，并且从输出上来看，我们确实是输出了正确的Entity信息</font>
> >
> > 拓展：经过实际上的测试，发现`requestTeamEntity = ecb.CreateEntity();`在这一步创建空物体的时候就**已经确定了该物体**的`Index`、`Version`、`HashCode`了，所以在任意地方输出都可以
>
> 服务端：直接在捕获后输出信息
>
> ```C#
> foreach (var (teamRequest, requestSource, requestEntity) 
>          in SystemAPI.Query<MobaTeamRequestRPC, ReceiveRpcCommandRequest>().WithEntityAccess())
> {
> 	Debug.Log($"Receive 0 : Index: {requestEntity.Index} Version: {requestEntity.Version} HashCode: {requestEntity.GetHashCode()}");
> ```
>
> <img class="half" src="/../images/unity/ECS框架学习笔记/数据包HashCode.png"></img>
>
> 为了实验的严谨性，该玩家是同时创建了客户端和服务端，这两个世界都是在他这一个程序上工作的。
>
> 但是从输出结果可以看出来，两个Entity确实不是同一个。
>
> 并且如果仔细想想，确实两个世界都不一样，怎么也不太可能是同一个Entitiy





---

### Ghost设置

在初始化角色前，先介绍一下客户端和服务端是怎么同步的——幽灵组件[GhostAuthoringComponent](https://docs.unity3d.com/Packages/com.unity.netcode@1.3/api/Unity.NetCode.GhostAuthoringComponent.html#fields)

<font color="red">需要实现服务器与客户端同步的物体，就需要挂载幽灵组件</font>，需要注意的点：

- 幽灵系统的作用：将两个世界里**创建**的`ICompnentData`复制一次到对面世界。仅仅只是复制，复制完后他们就没有任何联系了，甚至可以手动删除其中一个世界的组件。除非使用幽灵属性标记。
- 幽灵数据`[GhostField]`作用：将服务器的**数据**映射显示到客户端上，客户端并不能直接修改被标记为`[GhostField]`的数据。就算修改了，也会被系统快照强制覆盖掉
- `GhostAuthoringComponent`脚本**必须挂载在预制体**上，幽灵Entity通常是在运行的时候生成，而不是场景一开始就存在。当然，既然是Entity那就只能存在于子场景Eneities World中

> 可能会有一个误区：`[GhostField]`属性只是告诉系统这个数据的控制权应该完全交给服务器。
>
> - **如果你给服务器的Entity添加`IComponentData`，就算这个组件中没有`[GhostField]`，因为幽灵系统的存在，系统也会给客户端的Ghost添加该组件**
> - 更不要觉得如果一个`IComponentData`中有的数据有`[GhostField]`有的数据没有，~~系统就不会复制未被标记的数据~~。幽灵系统复制的`IComponentData`复制的是整个组件，而不是单独是数据。

> 脚本可以强行挂载在场景中一开始就存在的实体。这么做的话所有的配置都只能在预制体Asset本体上设置，场景中的每个实例化无法单独更改。

#### 配置：

<img class="half" src="/../images/unity/ECS框架学习笔记/GhostAuthoringComponent.png"></img>

- ` Importance`：数据优先级，数值越大越优先发送
- `SupportedGhostModes`：幽灵支持的模式，选择适合的模式能提供更好的优化，运行时无法更改此值
- [`DefaultGhostMode`](https://docs.unity3d.com/Packages/com.unity.netcode@1.3/api/Unity.NetCode.GhostMode.html)：模拟模式
  - `Interpolated`：轻量级，不在客户端上执行模拟。但他们的值是从最近几个快照的插值，此模式时间轴要慢于服务器。<font color='DarkGray'>与玩家关联不大的，如防御塔、小兵、水晶基地等。</font>
  - `Predicted`：完全由客户端预测。这种预测既昂贵又不权威，但它确实允许预测的幽灵更准确地与物理交互，并且它确实将他们的时间轴与当前客户端对齐。<font color='DarkGray'>与玩家交互强相关的才需要设置成这个，如英雄，飞行道具等。</font>
  - `OwnerPredicted`：由`Ghost Owner`（即服务端）预测，并且还会差值其他的客户端。<font color='DarkGray'>是上面两个模式的折中方案。</font>
- `OptimizationMode`：优化模式，针对是否会频繁的传递数据的优化
  - `Dynamic`：希望Ghost经常更改（即每帧）时使用。优化快照的大小，不执行更改检查，执行`delta-compression`（增量压缩）
  - `Static`：优化不经常改变的Ghosts。节省带宽，但是需要额外的CPU周期来执行检查是否有数据更改，如果更改了就发送数据给服务器。如果设置不对给经常改变的Ghost了，将增加带宽和cpu成本
- `HasOwner`：控制权是否是在玩家手上的，必须指定`NetwordId`的值
- `SupportAutoCommandTarget`：勾选后将标记为`[GhostField]`的数据自动生成缓冲数据发送给服务器

#### 组件

> <font color='red'>**再重复一遍，客户端和服务端连接的方式就只是靠`NetworkConnection`，Ghost系统也只不过是建立在`NetworkConnection`上面封装好的工具而已，最终都是需要通过`NetworkConnection`在服务端和客户端传递信息。**</font>

##### `GhostOwner`和`GhostOwnerIsLocal`

这两个组件在main entity和ghost entity上都绑定了

`GhostOwner`只有一个幽灵数据，由服务端控制，表示该entity是属于那个客户端的

```c#
[DontSupportPrefabOverrides]
[GhostComponent(SendDataForChildEntity = true)]
public struct GhostOwner : IComponentData
{
    [GhostField] public int NetworkId;
}
```

`GhostOwnerIsLocal`表面上看起来虽然是一个简单的可开关的标签，但其实是一个Ghost标签，客户端无法更改这个标签。其实该组件就是为了让客户端能快速定位到自己控制的Ghost entity而存在的。如果还嫌不够快的话，可以在自己创建一个单例标签。

```C#
public struct GhostOwnerIsLocal : IComponentData, IEnableableComponent { }
```

两个组件通力合作，在服务端上设置`GhostOwner.NetworkId = 2`之后，那么

- 对于该客户端而言：ghost entity的`GhostOwner.NetworkId = 2`的`GhostOwnerIsLocal`才是true，其他都是false
- 对于服务端而言：所有的`GhostOwnerIsLocal`都是true

#### 属性

##### 字段属性

- `[GhostField]`：完全由系统控制，系统会同步数值

##### Struct组件属性

- `[GhostComponent()]`：常用于`IcommandData`，与普通的`GhostComponent`不同，`IcommandData`默认不会从服务器同步到所有客户端。可设置参数如下：
  - `PrefabType`：设置该组件是否需要烘焙到客户端上，例如：
    - `GhostPrefabType.AllPredicted`：`Predicted`模式的实体，客户端和服务端都会烘焙；`Interpolated`和`Owner Predicted`不会烘焙客户端
    - `GhostPrefabType.All`（默认选项）：所有类型，客户端、服务端都会烘焙
  - `OwnerSendType`：控制数据需要发送给那些客户端。<font color="DarkGray">对无服务没有影响，仅仅只是控制是否会 发送给客户端而已，比如计算的一些中间值就可以不用同步给客户端</font>
    - `SendToNonOwner`：表示该数据只会发送给非拥有者的其他客户端
    - `None`：表示所有客户端都不会发送。适合一些中转数据，这类数据对客户端没影响，客户端也不需要这种数据，以减少带宽





---

### 初始化角色

#### 前言

在给物体添加组件时先思考一下，这个客户端和服务端是否都需要用到这个组件

可以创建三个初始化system：客户端、服务端和共同的。例如，输入系统不需要在服务端运行，那么就只用将其在客户端system上初始化就OK了

> 如果使用了Ghost，那么在Authoring中烘焙的所有组件都同时会存在在客户端和服务端上

```C#
// [UpdateInGroup(typeof(SimulationSystemGroup), OrderFirst = true)]	// 共同初始化
// [WorldSystemFilter(WorldSystemFilterFlags.ClientSimulation | WorldSystemFilterFlags.ThinClientSimulation)]		// 只在客户端上初始化
// [WorldSystemFilter(WorldSystemFilterFlags.ServerSimulation)]      // 只在服务端运行
public partial struct InitializeCharacterSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var ecb = new EntityCommandBuffer(Allocator.Temp);
        foreach (var (physicsMass, mobaTeam, newCharacterEntity) in SystemAPI.Query<RefRW<PhysicsMass>, MobaTeam>().WithAll<NewChampTag>().WithEntityAccess())
        {
            // ...
            // 初始化角色
            // ...
            ecb.RemoveComponent<NewChampTag>(newCharacterEntity);	// 非常经典的"工具人"标签
        }
        ecb.Playback(state.EntityManager);
    }
}
```

#### 物理

添加下面两个组件

{% grouppicture 2-2 %}

<img class="half" src="/../images/unity/ECS框架学习笔记/Rigibody.png"></img>

<img class="half" src="/../images/unity/ECS框架学习笔记/Physics.png"></img>

{% endgrouppicture %}

- `Rigibody`：
  - `Use Gravity`：为了避免服务端和客户端不同步，我们不能使用物理系统。关闭后就会多出`Physics Gravity Factor`组件（暂时不知道是干嘛的？）
  - `Is Kinematic`：启用后物理系统将不能施加力来移动或旋转物体，而只能改变Transform来移动旋转物体
  
  ```C#
  physicsMass.ValueRW.InverseInertia = float3.zero;      // 设置惯性为无限
  ```
- `Physcis Shape`：自定义物体包围盒，通常是在预制体的时候设置好。<font color="DarkGray">该组件需要在`Package Manage`的`Unity Physics`的`Samples`中下载`Custom Physics Authoring`</font>

#### 颜色

在烘焙的时候添加`URPMaterialPropertyBaseColor`组件或者直接在Inpector面板添加

<img class="half" src="/../images/unity/ECS框架学习笔记/URPMaterialPropertyBaseColor.png"></img>

```C#
var teamColor = mobaTeam.Value switch
{
    TeamType.Blue => new float4(0, 0, 1, 1),
    TeamType.Red => new float4(1, 0, 0, 1),
    _ => new float4(1)
};

ecb.SetComponent(newCharacterEntity, new URPMaterialPropertyBaseColor{ Value = teamColor });	// 设置颜色
```



#### 优化

就目前来说，这个初始化System可以只在客户端上运行？



---

### 输入

- 客户端唯一拥有的权限就是输入
- 但判断你输入的内容是否有效合法，决定权还是在服务器
- 输入数据是客户端和服务器之间的非常频繁传递的数据
- 有一个专门用来传递的组件`IInputComponentData`，比`ICommandData`要好用

> [`ICommandData`](https://docs.unity3d.com/Packages/com.unity.netcode@1.3/api/Unity.NetCode.ICommandData.html)
>
> - 如果需要频繁的从客户端向服务器发送数据应该使用`ICommandData`而不是`RPC`，`ICommandData`有优化
>
> - 类似于一个`Dynamic Buffer`动态缓冲器，他将保存最后64`NetWorkTick`的数据
>
> - 需要设置每帧获取多少Tick
>
> ```C#
> public struct DamageThisTick : ICommandData{
>     public NetworkTick Tick {get; set;}
>     public int Value
> }
> ```
>
> `IInputComponentData`不需要设置Tick，系统自动完成
>
> `InputEvent`是存储在`IInputComponentData`中的输入事件。服务器一般为 60帧，如果客户端为120帧，服务器很有可能检测不到玩家的输入，`InputEvent`针对这个问题进行的优化。



#### 使用方法

从玩家输入到游戏中显示效果，需要两个系统来实现效果，拿移动来举例

- `MoveInputSystem`：在客户端上运行，获取玩家输入
  - 添加到`GhostInputSystemGroup`中，该Group只存在于Client World中
  - 需要监听输入，并将输入转换成`IInputComponentData`组件上的数据，存放在该客户端`GhostOwnerIsLocal`的Ghost Entity上
  - unity会自动同步该数据，即使你没有使用`[GhostField]`修饰数据
- `MoveSystem`：同时在客户端和服务端上运行，执行玩家的命令
  - 添加到`PredictedSimulationSystemGroup`中，客户端和服务端都会运行，并且会模拟预测数据
  - unity将数据从客户端同步到服务端之后，就可以捕获到数据并执行命令了



##### 传递普通数据：

设置需要传递的数据

```C#
// [GhostComponent(PrefabType = GhostPrefabType.AllPredicted)]		// 可以优化需要传递的对象
public struct ChampMoveTargetPosition : IInputComponentData
{
    // [GhostField(Quantization = 0)]		// 设置精度，0表示全精度；1表示整数；10表示0.1f
    public float3 Value;		// IInputComponentData会自动将自身的数据修饰为[GhostField]
}
```

将system添加到`GhostInputSystemGroup`中并。然后设置数值，系统会自动帮我们实现同步

```C#
[UpdateInGroup(typeof(GhostInputSystemGroup))]  // 添加到输入组，该组只存在于Client中
public partial class ChampMoveInputSystem : SystemBase
{
    protected override void OnStartRunning()
    {
        // 以委托事件的形式监听输出
        PlayerInputSystem.Instance.SelectMovePositionEvent += OnSelectMovePosition;
    }

    protected override void OnStopRunning()
    {
        PlayerInputSystem.Instance.SelectMovePositionEvent -= OnSelectMovePosition;
    }
    
    private void OnSelectMovePosition(InputAction.CallbackContext obj)
    {
        var champEntity = SystemAPI.GetSingletonEntity<OwnerChampTag>();
        EntityManager.SetComponentData(champEntity, new ChampMoveTargetPosition()
        {
            Value = closestHit.Position		// 设置数值，unity会自动将其同步到main entity上
        });
    }
}
```

##### 传递`InputEvent`数据

定义`IInputComponentData`和`InputEvent`，并将其烘焙到Entitiy上

```c#
// [GhostComponent(PrefabType = GhostPrefabType.AllPredicted)]		// 可以优化需要传递的对象
public struct AbilityInput : IInputComponentData
{
    // [GhostField]
    public InputEvent AoeAbility;		// IInputComponentData会自动将自身的数据修饰为[GhostField]
}
```

```C#
[UpdateInGroup(typeof(GhostInputSystemGroup))]  // 添加到输入组，该组只存在于Client中
public partial class AbilityInputSystem : SystemBase
{
    protected override void OnUpdate()
    {  
        var newAbilityInput = new AbilityInput();			// 因为是结构体是值类型，所以不会有GC；

        if (PlayerInputSystem.Instance.QKeyWasPressedThisFrame)		// 监听输入
        {
            newAbilityInput.AoeAbility.Set();		// Set()表示加一，即被按下了
        }

        foreach (var abilityInput in SystemAPI.Query<RefRW<AbilityInput>>())
        {
            abilityInput.ValueRW = newAbilityInput;		// 设置数值，unity会自动将其同步到main entity上
        }
    }
}
```

`InputEvent`类似一个计数器，客户端使用`Set()`之后。
服务端检测到其大于0，那么就会判定为输入了，同时将其复原成0。
这样就避免了服务器帧率没有客户端高，而引发的监听不到输入的问题了。
`InputEvent`常用在类似按钮的触发事件，移动摇杆这类常用的移动输入直接使用数值就OK了

> 这里说个题外话：关于`var newAbilityInput = new AbilityInput();`
>
> - 因为结构体是值类型，所以在`OnUpdate`执行完后会直接释放掉，不涉及垃圾回收（也就是GC）
> - 由于栈的分配效率非常高效，即使`OnUpdate`每帧都在调用，数据量不大的话也不会对性能有影响



---

### 销毁

步骤：

1. 在预制体上烘焙`DestoryOnTimer`，<font color="red">**预设**</font>物体多久后销毁

2. 客户端和服务端都会运行的`InitializeDestoryOnTimerSystem`捕获拥有`DestoryOnTimer`组件的实体，并<font color="red">**计算**</font>该实体在多少Tick的时候销毁，将计算的事件存储在`DestroyAtTick`的Ghost数据上

   - 服务器计算时间不能以`deltaTime`（不够稳定）或`frame`（客户端和服务端会不一致）
   - 而是使用`ServerTick`，说简单点其实也是帧，只不过是特指服务器的帧，默认为60Tick/秒

3. 客户端和服务端都会运行的`DestroyOnTimerSystem`捕获拥有`DestroyAtTick`组件的实体，并<font color="red">**判断**</font>该实体是否已达到销毁时间，达到销毁时间后挂载`DestroyEntityTag`标签

   - 该system只是添加标签，并不是直接销毁
   - 为什么不直接销毁？因为**凡是涉及到客户端表现的都需要做预测**，也就是得放置在`PredictedSimulationSystemGroup`中

4. 放置在`PredictedSimulationSystemGroup`<font color='DarkGray'>（预测组——服务端和客户端都会预测）</font>中的`DestroyEntitySystem`捕获拥有`DestroyEntityTag`标签的实体进行<font color='red'>**处理**</font>。暂时没有很好的办法使客户端和服务端同时进行销毁，当前的做法如下：

   - 服务端：直接摧毁
   - 客户端：将物体移动到不可见的位置，并等待服务器同步

   从下图可看出，有一半的次数客户端要晚于服务端摧毁，然而实际运用起来可能不止一半

   <img class="half" src="/../images/unity/ECS框架学习笔记/销毁.gif"></img>

共涉及两个组件、一个标签、三个系统

```c#
public struct DestroyAtTick : IComponentData
{
    [GhostField] public NetworkTick Value;		// 应在服务器的第几Tick销毁
}
```

```C#
public struct DestroyEntityTag : IComponentData { }		// 达到了被销毁时间的entitiy
```

#### 步骤一：预设烘焙

```C#
public struct DestroyOnTimer : IComponentData
{
    public float Value;		// 烘焙预设的销毁时间
}
```

#### 步骤二：计算销毁时间

```c#
// 默认客户端和服务端都会执行，计算多少Tick销毁，并添加DestroyAtTick
public partial struct InitializeDestroyOnTimerSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var ecb = new EntityCommandBuffer(Allocator.Temp);
        // 获取服务器帧率：默认60
        var simulationTickRate = NetCodeConfig.Global.ClientServerTickRate.SimulationTickRate;
        var currentTick = SystemAPI.GetSingleton<NetworkTime>().ServerTick;         // 当前服务器运行多少Tick

        foreach (var (destroyOnTimer, entity) in SystemAPI.Query<DestroyOnTimer>().WithNone<DestroyAtTick>()
                     .WithEntityAccess())	// 捕获被预设为销毁的物体
        {
            var lifetimeInTicks = (uint)(destroyOnTimer.Value * simulationTickRate);
            var targetTick = currentTick;
            targetTick.Add(lifetimeInTicks);        // 设置该entity应该在服务器的第几帧销毁
            ecb.AddComponent(entity, new DestroyAtTick { Value = targetTick });
        }

        ecb.Playback(state.EntityManager);
    }
}
```

#### 步骤三：判断是否达到销毁Tick

```c#
// 默认客户端和服务端都会执行，判断物体是否达到销毁Tick，并添加DestroyEntityTag
public partial struct DestroyOnTimerSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        // 在结束的时候添加标签
        var ecbSingleton = SystemAPI.GetSingleton<EndSimulationEntityCommandBufferSystem.Singleton>();
        var ecb = ecbSingleton.CreateCommandBuffer(state.WorldUnmanaged);

        var currentTick = SystemAPI.GetSingleton<NetworkTime>().ServerTick;

        foreach (var (destroyAtTick, entity) in SystemAPI.Query<DestroyAtTick>().WithAll<Simulate>()
                     .WithNone<DestroyEntityTag>().WithEntityAccess())	// 捕获有销毁时间的物体
        {
            if (currentTick.Equals(destroyAtTick.Value) || currentTick.IsNewerThan(destroyAtTick.Value))
                ecb.AddComponent<DestroyEntityTag>(entity);		// Tick大于等于当前服务器Tick就添加标签
        }
    }
}
```

#### 步骤四：处理服务端和客户端

```c#
// 预测，客户端和服务端都会预测
[UpdateInGroup(typeof(PredictedSimulationSystemGroup), OrderLast = true)]
public partial struct DestroyEntitySystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var networkTime = SystemAPI.GetSingleton<NetworkTime>();

        // 在开始的时候销毁
        var ecbSingleton = SystemAPI.GetSingleton<BeginSimulationEntityCommandBufferSystem.Singleton>();
        var ecb = ecbSingleton.CreateCommandBuffer(state.WorldUnmanaged);

        foreach (var (transform, entity) in SystemAPI.Query<RefRW<LocalTransform>>()
                     .WithAll<DestroyEntityTag, Simulate>().WithEntityAccess())
        {
            if (state.World.IsServer())			// 服务器直接销毁
                ecb.DestroyEntity(entity);
            else								// 客户端移动到不可见位置，等待服务器同步
                transform.ValueRW.Position = new float3(999f, 999f, 999f);
        }
    }
}
```



---

### 伤害

步骤：

1. <font color='red'>**预设烘焙**</font>：
   - 可造成伤害实体（飞行物、刀剑等）：
     - `DamageOnTrigger`：设置伤害量
     - `AlreadyDamagedEntity`：存储造成伤害的entity，防止重复造成伤害
   - 可受伤的实体（英雄、防御塔、小兵等）：
     - `DamageBufferElement`：存储伤害值
     - `DamageThisTick`：记录在服务器的多少帧受到多少伤害，并将伤害应用到实体上
2. <font  color='red'>**监听**</font>碰撞：使用`ITriggerEventsJob`监听碰撞，并执行以下处理
   - 将伤害值添加到受击者的`DamageBufferElement`伤害缓存池中
   - 将受击者添加到攻击者的`AlreadyDamagedEntity`中，防止重复计算伤害
3. <font color='red'>**计算**</font>伤害：捕获`DamageBufferElement`并将其数值和当前Tick存储在`DamageThisTick`中
4. <font color='red'>**实施**</font>伤害：捕获`DamageThisTick`并判断是否是当前帧，只有是当前帧的伤害才实施

共涉及4个组件和三个系统，所有系统都是在`PredictedSimulationSystemGroup`预测组上运行的

####  第一步：预设烘焙

```C#
public struct DamageOnTrigger : IComponentData
{
    public int Value;			// 烘焙到可造成伤害的实体上，设置其伤害量
}
```

```c#
public struct AlreadyDamagedEntity : IBufferElementData
{
    public Entity Value;		// 烘焙到可造成伤害的实体上，记录伤害过的实体，避免重复伤害
}
```

```C#
[GhostComponent(PrefabType = GhostPrefabType.AllPredicted)]
public struct DamageBufferElement : IBufferElementData
{
    public int Value;		// 烘焙到可受伤的对象上，表示该物体是可受伤的。该组件只是暂存伤害，并不直接应用
}
```

```C#
// 发送给除entity控制者以外的所有其他客户端Ghost entity
[GhostComponent(PrefabType = GhostPrefabType.AllPredicted, OwnerSendType = SendToOwnerType.SendToNonOwner)]
public struct DamageThisTick : ICommandData		// 烘焙到可受伤的实体上
{
    public NetworkTick Tick { get; set; }
    public int Value;
}
```

#### 第二步：监听碰撞

注意：使用的是`ITriggerEventsJob`而不是普通的`IJobEntity`

```c#
[UpdateInGroup(typeof(PhysicsSystemGroup))]     // 涉及到物体碰撞（即客户端表现），所以放在PhysicsSystemGroup之中
[UpdateAfter(typeof(PhysicsSimulationGroup))]
public partial struct DamageOnTriggerSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var simulationSingleton = SystemAPI.GetSingleton<SimulationSingleton>();
        state.Dependency = job.Schedule(simulationSingleton, state.Dependency);*/
        bool isClient = state.World.IsClient();
        var ecbSingleton = SystemAPI.GetSingleton<EndSimulationEntityCommandBufferSystem.Singleton>();
        var damageOnTriggerJob = new DamageOnTriggerJob
        {
            DamageOnTriggerLookup = SystemAPI.GetComponentLookup<DamageOnTrigger>(true),
            TeamLookup = SystemAPI.GetComponentLookup<MobaTeam>(true),
            AlreadyDamagedLookup = SystemAPI.GetBufferLookup<AlreadyDamagedEntity>(true),
            DamageBufferLookup = SystemAPI.GetBufferLookup<DamageBufferElement>(true),
            ECB = ecbSingleton.CreateCommandBuffer(state.WorldUnmanaged),
            isClient = isClient,
        };
        var simulationSingleton = SystemAPI.GetSingleton<SimulationSingleton>();
        state.Dependency = damageOnTriggerJob.Schedule(simulationSingleton, state.Dependency);
    }
}
public struct DamageOnTriggerJob : ITriggerEventsJob        // 不是普通的IJobEntity
{	// 队伍
    [ReadOnly] public ComponentLookup<MobaTeam> TeamLookup;
    // 伤害量，该组件是被烘焙在可造成伤害的实体上
    [ReadOnly] public ComponentLookup<DamageOnTrigger> DamageOnTriggerLookup;
    // 受到多少伤害，该组件是被烘焙在可受到伤害的实体上
    [ReadOnly] public BufferLookup<DamageBufferElement> DamageBufferLookup;
	// 已经受到过伤害的实体，避免重复伤害
    [ReadOnly] public BufferLookup<AlreadyDamagedEntity> AlreadyDamagedLookup;
    public EntityCommandBuffer ECB;
    
    public void Execute(TriggerEvent triggerEvent)
    {
        Entity damageDealingEntity;         // 伤害来源，即飞行物
        Entity damageReceivingEntity;       // 受击者

        // 判断两个实体，哪个是伤害来源，哪个是受击者
        if (DamageBufferLookup.HasBuffer(triggerEvent.EntityA) &&
            DamageOnTriggerLookup.HasComponent(triggerEvent.EntityB))
        {
            damageReceivingEntity = triggerEvent.EntityA;
            damageDealingEntity = triggerEvent.EntityB;
        }
        else if (DamageOnTriggerLookup.HasComponent(triggerEvent.EntityA) &&
                 DamageBufferLookup.HasBuffer(triggerEvent.EntityB))
        {
            damageDealingEntity = triggerEvent.EntityA;
            damageReceivingEntity = triggerEvent.EntityB;
        }
        else return;     // 如果碰撞的两个没有伤害组件直接返回

        if (TeamLookup.TryGetComponent(damageDealingEntity, out var damageDealingTeam) &&
            TeamLookup.TryGetComponent(damageReceivingEntity, out var damageReceivingTeam))
        {
            if (damageDealingTeam.Value == damageReceivingTeam.Value) return;   // 没有友伤
        }

        var alreadyDamagedBuffer = AlreadyDamagedLookup[damageDealingEntity];

      	// 这里客户端有一个BUG，由于ECB没有及时的将enitiy添加到队列中，会导致重复添加伤害，但服务端是好的
        foreach (AlreadyDamagedEntity alreadyDamagedEntity in alreadyDamagedBuffer)
            if (alreadyDamagedEntity.Value.Equals(damageReceivingEntity)) return; // 判断是否已经造成过伤害了

        // 将伤害量缓冲到受击者实体上
        var damageOnTrigger = DamageOnTriggerLookup[damageDealingEntity];
        ECB.AppendToBuffer(damageReceivingEntity, new DamageBufferElement {Value = damageOnTrigger.Value }); 
        // 将受击者保存到伤害来源实体上
        ECB.AppendToBuffer(damageDealingEntity, new AlreadyDamagedEntity { Value = damageReceivingEntity });
    }
}
```

#### 第三步：计算伤害

```c#
[UpdateInGroup(typeof(PredictedSimulationSystemGroup), OrderLast = true)]
public partial struct CalculateFrameDamageSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var currentTick = SystemAPI.GetSingleton<NetworkTime>().ServerTick;

        foreach (var (damageBuffer, damageThisTickBuffer) in SystemAPI
                     .Query<DynamicBuffer<DamageBufferElement>, DynamicBuffer<DamageThisTick>>()
                     .WithAll<Simulate>())
        {
            if (damageBuffer.IsEmpty)   // 如果为空
            {
                // 配合下方的GetDataAtTick方法，需要不停的赋值
                damageThisTickBuffer.AddCommandData(new DamageThisTick { Tick = currentTick, Value = 0 });
            }
            else
            {
                var totalDamage = 0;
                // 获取最靠近当前帧的上一帧的伤害，因为上面一直在设置为0，所以大多数这里捕获的值都是0
                // TODO: 讲道理，并不知道这么做有什么用？
                if (damageThisTickBuffer.GetDataAtTick(currentTick, out var damageThisTick))
                {
                    totalDamage = damageThisTick.Value;         // 加上最近一帧的伤害
                }

                foreach (var damage in damageBuffer)
                {
                    totalDamage += damage.Value;		// 累加缓冲器中的伤害值
                }

                // 将伤害
                damageThisTickBuffer.AddCommandData(new DamageThisTick 
                                                    { Tick = currentTick, Value = totalDamage });
                damageBuffer.Clear();
            }
        }
    }
}
```

#### 第四步：实施伤害

```c#
[UpdateInGroup(typeof(PredictedSimulationSystemGroup), OrderLast = true)]
[UpdateAfter(typeof(CalculateFrameDamageSystem))]       // 在计算伤害量之后执行
public partial struct ApplyDamageSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var currentTick = SystemAPI.GetSingleton<NetworkTime>().ServerTick;
        var ecb = new EntityCommandBuffer(Allocator.Temp);

        foreach (var (currentHitPoints, damageThisTickBuffer, entity) in SystemAPI
                     .Query<RefRW<CurrentHitPoints>, DynamicBuffer<DamageThisTick>>().WithAll<Simulate>()
                     .WithEntityAccess())
        {
            if (!damageThisTickBuffer.GetDataAtTick(currentTick, out DamageThisTick damageThisTick)) continue;
            // 过滤掉不是当前帧的伤害，因为本系统是在计算伤害系统之后运行的，所以这个是可行的
            if (damageThisTick.Tick != currentTick) continue;
            currentHitPoints.ValueRW.Value -= damageThisTick.Value;

            if (currentHitPoints.ValueRO.Value <= 0)
            {
                ecb.AddComponent<DestroyEntityTag>(entity);		// 如果血量低于0就添加销毁标签
            }
        }
        ecb.Playback(state.EntityManager);
    }
}
```

### 技能CD





















