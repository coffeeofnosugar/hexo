---
title: 【Unity】ECS框架学习笔记（三）——Tick
date: 2024-09-20 12:036:06
tags:
  - Unity
  - ECS
---

由于这个比较重要，而且不宜理解，所以这里单独从第二篇文章中单独拎出来展示。

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

    <img class="half" src="/../images/unity/ECS框架学习笔记/学习笔记二/IsFirstTimeFullyPredictingTick用法.png"></img>

  {% grouppicture 2-2 %}

  <img class="half" src="/../images/unity/ECS框架学习笔记/学习笔记二/服务端Tick与Update.png"></img>

  <img class="half" src="/../images/unity/ECS框架学习笔记/学习笔记二/客户端Tick与Update.png"></img>

  {% endgrouppicture %}

- 服务端与客户端的Tick并不同步。这应该就是延迟的由来？

  {% grouppicture 2-2 %}

  <img class="half" src="/../images/unity/ECS框架学习笔记/学习笔记二/服务端Tick.png"></img>

  <img class="half" src="/../images/unity/ECS框架学习笔记/学习笔记二/客户端Tick.png"></img>

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

