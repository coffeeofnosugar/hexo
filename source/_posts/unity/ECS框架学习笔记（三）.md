---
title: 【Unity】ECS框架学习笔记（三）——多人联网
date: 2024-09-20 12:036:06
tags:
  - Unity
  - ECS
---

### 夺回生成世界的控制权

在下载NetCode包体之后，启动游戏的时候Entities会生成ClientWorld和ServerWorld两个世界。
但我们玩家是先进入主菜单，再进入游戏，所以最开始的时候不用生成ServerWorld。

将`Overide Automatic Netcode Bootstrap`组件挂载到场景中的任意物体上并选择`Disable Automatic Bootstrap`就OK了
因为我们要控制所有场景的世界生成，所以所有场景都需要挂载

<img class="half" src="/../images/unity/ECS框架学习笔记/Bootstrapper.png"></img>

挂载之后，启动场景时只会生成`Default World`。
然后我们在进入游戏的时候删除掉`Default World`，生成`Client World`和`Server World`就OK了。



---

### 删除默认世界

玩家进入游戏后默认是进入`Default World`，是多余的需要删掉，正好在切场景的时候删除掉所有内容

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

<img class="half" src="/../images/unity/ECS框架学习笔记/DefaultWorld.png"></img>

<img class="half" src="/../images/unity/ECS框架学习笔记/Client&ServerWorld.png"></img>



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
public struct ClientTeamRequest : IComponentData
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

    World.DefaultGameObjectInjectionWorld = clientWorld;	// 将对Default World世界的操作同步到Client World，以免每次操作都要使用Client的API

    var team = _teamDropdown.value switch		// 设置传递给Entities的信息
    {
        0 => TeamType.AutoAssign,
        1 => TeamType.Blue,
        2 => TeamType.Red,
        _ => TeamType.None
    };
    
	// 将用户在GameObject中选择的队伍传递到Entities中，！！！注意：这里并没有向服务端发送请求
    var teamRequestEntity = clientWorld.EntityManager.CreateEntity();
    clientWorld.EntityManager.AddComponentData(teamRequestEntity, new ClientTeamRequest()
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
        state.RequireForUpdate<ClientTeamRequest>();        // 获取在登入界面创建的组件
    }

    public void OnUpdate(ref SystemState state)
    {
        // 获取在登入界面创建的组件
        var requestedTeam = SystemAPI.GetSingleton<ClientTeamRequest>().Value;

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

<img class="half" src="/../images/unity/ECS框架学习笔记/网络连接-客户端.png"></img>

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

### 服务端接收玩家进入请求

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
            ecb.DestroyEntity(requestEntity);   // 客户端发送的请求包，但这里需要手动销毁。是同一个实体？
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
            // 设置该实例化角色控制的客户端ID
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
> // 当玩家断线重连时，系统将摧毁旧的服务端Entity，并创建新的服务端Entity
> ecb.AppendToBuffer(requestSource.SourceConnection, new LinkedEntityGroup(){ Value = newChamp });
> // ...
> // 其他设置，如position、队伍、名称等，设置名称后可以直接在`Hierarchy`窗口看到
> // ...
> ```
>
> - `GhostOwner`：设置改服务器实体的控制者是哪个客户端
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
> <img class="half" src="/../images/unity/ECS框架学习笔记/服务端.png"></img>



---

### RPC小结

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

### 英雄预制体准备

普通的Authoring烘焙脚本就不说了，只讲讲幽灵组件[GhostAuthoringComponent](https://docs.unity3d.com/Packages/com.unity.netcode@1.3/api/Unity.NetCode.GhostAuthoringComponent.html#fields)

<font color="red">需要实现服务器与客户端同步的物体，就需要挂载幽灵组件</font>，需要注意的点：

- 幽灵的作用将服务器的数据映射显示到客户端上
- 玩家控制的其实的幽灵Entities
- 幽灵必须挂载在预制体上，通常是在运行的时候生成，并且只能是生成在子场景
- 客户端并不能直接设置幽灵的数据，只是被`netword snapshot`覆盖了

<img class="half" src="/../images/unity/ECS框架学习笔记/GhostAuthoringComponent.png"></img>

- ` Importance`：数据优先级，数值越大越优先发送
- `SupportedGhostModes`：幽灵支持的模式，选择适合的模式能提供更好的优化，运行时无法更改此值
- [`DefaultGhostMode`](https://docs.unity3d.com/Packages/com.unity.netcode@1.3/api/Unity.NetCode.GhostMode.html)：模拟模式
  - `Interpolated`：轻量级，不在客户端上执行模拟。但他们的值是从最近几个快照的插值，此模式时间轴要慢与服务器
  - `OwnerPredicted`：由`Ghost Owner`（即服务端）预测，并且还会差值其他的客户端
  - `Predicted`：完全由客户端预测。这种预测既昂贵又不权威，但它确实允许预测的幽灵更准确地与物理交互，并且它确实将他们的时间轴与当前客户端对齐。
- `OptimizationMode`：优化模式，针对是否会频繁的传递数据的优化
  - `Dynamic`：希望Ghost经常更改（即每帧）时使用。优化快照的大小，不执行更改检查，执行`delta-compression`（增量压缩）
  - `Static`：优化不经常改变的Ghosts。节省带宽，但是需要额外的CPU周期来执行检查是否有数据更改，如果更改了就发送数据给服务器。如果设置不对给经常改变的Ghost了，将增加带宽和cpu成本

- `HasOwner`：控制权是否是在玩家手上的，必须指定`NetwordId`的值
- `SupportAutoCommandTarget`：勾选后将标记为`[GhostField]`的数据自动生成缓冲数据发送给服务器

