---
title: 【Linux】Linux dotnet
date: 2023-08-22 10:02:06
tags: Linux
---

# 安装

不同ubuntu版本的net版本都有不同的命令，具体可以直接访问[官方下载渠道](https://learn.microsoft.com/zh-cn/dotnet/core/install/linux-ubuntu-install?tabs=dotnet10&pivots=os-linux-ubuntu-2204)

在 ubuntu 22.04 中下载 .net9 流程如下



> .NET在 Ubuntu .NET backports 包存储库中提供。 若要添加存储库，请打开终端并运行以下命令：
>
> ```bash
> sudo add-apt-repository ppa:dotnet/backports
> ```
>
> 
>
> ### 安装 SDK
>
> .NET SDK 允许使用 .NET 开发应用。 如果安装 .NET SDK，则无需安装相应的运行时。 若要安装 .NET SDK，请运行以下命令：
>
> ```bash
> sudo apt-get update && \
>   sudo apt-get install -y dotnet-sdk-9.0
> ```
>
> 若要了解如何使用 .NET CLI，请参阅 [.NET CLI 概述](https://learn.microsoft.com/zh-cn/dotnet/core/tools/)。
>
> 
>
> ### 安装运行时
>
> ASP.NET Core运行时允许您运行那些未包含运行时的.NET应用程序。 以下命令安装 ASP.NET Core运行时，这是.NET最兼容的运行时。 在终端中，运行以下命令：
>
> ```bash
> sudo apt-get update && \
>   sudo apt-get install -y aspnetcore-runtime-9.0
> ```
>
> 作为 ASP.NET Core 运行时的替代方法，可以安装不包含 ASP.NET Core支持的 .NET Runtime：将上一命令中的 `aspnetcore-runtime-9.0` 替换为 `dotnet-runtime-9.0`：
>
> ```bash
> sudo apt-get install -y dotnet-runtime-9.0
> ```





---

# dotnet诊断工具

## 安装

```bash
dotnet tool install -g dotnet-counters
dotnet tool install -g dotnet-gcdump
```

验证

```bash
dotnet-counters --version
```

不安装的话可以使用最简单的命令先查看一下

```bash
cat /proc/50594/status | grep VmRSS
```

## 查看

```bash
dotnet-counters monitor -p 50594
```

面板会变成

```bash
Press p to pause, r to resume, q to quit.
    Status: Running

Name                                                                                                                                                                                                                                      Current Value
[System.Runtime]
    dotnet.assembly.count ({assembly})                                                                     149
    dotnet.exceptions ({exception})
        error.type
        -----------------------
        BadHttpRequestException                                                                             4
    #  服务器启动以来 GC 次数
    dotnet.gc.collections ({collection})
        gc.heap.generation
        ------------------
        gen0                                                                                           209,056
        gen1                                                                                           107,853
        gen2                                                                                               721
    # 服务器启动以来累计分配量   8.8TB
    dotnet.gc.heap.total_allocated (By)                                                                8.8668e+12
    # 堆碎片，详情解锁见下面
    dotnet.gc.last_collection.heap.fragmentation.size (By)
        gc.heap.generation
        ------------------
        gen0                                                                                                 0
        gen1                                                                                           111,336
        gen2                                                                                            3.9331e+08
        loh                                                                                        15,980,504
        poh                                                                                                 0
    # 当前堆大小————————最重要的数据——————最近一次GC结束后，各代还剩多少对象
    dotnet.gc.last_collection.heap.size (By)
        gc.heap.generation
        ------------------
        gen0                                                                                                 0
        gen1                                                                                         5,212,680   # 5MB
        gen2                                                                                            4.5019e+09  # 4.5GB
        loh                                                                                        73,186,232
        poh                                                                                         4,157,640
    # 当前 GC 向操作系统申请的总内存
    dotnet.gc.last_collection.memory.committed_size (By)                                                4.6749e+09
    dotnet.gc.pause.time (s)                                                                             6,179.84
    dotnet.jit.compilation.time (s)                                                                     5,113.575
    dotnet.jit.compiled_il.size (By)                                                                    4.6519e+08
    dotnet.jit.compiled_methods ({method})                                                          19,333,691
    # 锁竞争次数，对于运行了19小时的服务器不算离谱
    dotnet.monitor.lock_contentions ({contention})                                                   6,563,268
    dotnet.process.cpu.count ({cpu})                                                                         4
    dotnet.process.cpu.time (s)
        cpu.mode
        # system vs user : 16% vs 84% 很正常
        --------
        # 内核消耗CPU的时间，如Socket、文件IO、网络发送、epoll、线程切换
        system                                                                                          10,128.697
        # 我的代码消耗CPU的时间，如Update()、Move()、Battle()、AI()
        user                                                                                            53,776.818
    # 当前真正占用物理内存，就是 Linux 的 RES VmRSS对应的数据。
    dotnet.process.memory.working_set (By)                                                              4.8229e+09
    # 任务堆积数量
    dotnet.thread_pool.queue.length ({work_item})                                                           0
    # 线程池线程数
    dotnet.thread_pool.thread.count ({thread})                                                               6
    dotnet.thread_pool.work_item.count ({work_item})                                                    2.1725e+08
    dotnet.timer.count ({timer})                                                                             5
```

> 解释
> gen0-->gen1-->gen2 为代系，gen0是刚创建的，gen1是经过几次GC后还活着的，gen2是活了很久的
>
> loh = Large Object Heap 大对象堆，如果对象>85000字节就会进入LOH
>
> pho = Pinned Object Heap 固定对象堆，一般游戏服务器用的很少
>
> 
>
> 堆碎片:
>
> 类似：`[对象][空洞][对象][空洞][对象]`GC回收后产生的空隙
>
> 4.5GB对象中间有393MB空洞不算特别严重
>
> 

