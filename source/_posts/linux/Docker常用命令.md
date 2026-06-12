---
title: 【Linux】Docker常用命令
date: 2025-04-19 19:03:06
tags:
 - Linux
 - Docker
---

如果用户权限不足无法使用docker命令，需要先使用权限更高的用户将该用户分配到docker组中`sudo usermod -aG docker {usernam}`

> 注意：
>
> 如果使用的是VSCode连接的服务器，可能会出现每次连接后该用户的分组（输入`Gropos`查看）不是最新的问题。
>
> 原因：
>
> VSCode Remote SSH 会:
>
> - 保持长连接
>
> - 复用 ssh control master
>
> - 后台常驻 vscode-server
>
> 你以为重新连接了，其实还是原来的ssh session
>
> 解决方法：
>
> 原因清楚之后，就很好解决了，只需要将VSCode Remote SSH完全断开就好了
>
> - 在VSCode中使用快捷键`Ctrl`+`Shift`+`p`
> - 输入`Remote-SSH: Kill VS Code Server on Host`
> - 选择你的服务器，并输入密码
> - 重新启动VSCode

### 帮助命令

[官方文档](https://docs.docker.com/engine/reference/run/)

| docker  version    | 显示docker的版本信息                       |
| ------------------ | ------------------------------------------ |
| docker  info       | 显示docker的系统信息，包括镜像和容器的数量 |
| docker 命令 --help | 帮助命令                                   |

### 镜像命令

| 查看镜像 | docker  images             |                                             |
| -------- | -------------------------- | ------------------------------------------- |
|          | -a, --all                  | 查看所有镜像                                |
|          | -q, --quiet                | 只显示镜像ID                                |
| 搜索镜像 | docker  search <imageName> |                                             |
|          | -f, --filter               | 筛选条件eg:  --filter=STARS=300 收藏大于300 |
| 下载镜像 | docker  pull <imageName>   |                                             |
|          | docker  pull mysql:5.7     | 指定版本                                    |
| 删除镜像 | docker  rmi -f <imageId>   |                                             |
|          | -f  $(docker images -aq)   | 删除所有镜像                                |

运行临时容器`docker run --rm -i grafana/k6 run - < k6-test.js`

- `run`：运行容器
- `--rm`：运行后自动删除容器
- `-i`：可以在容器运行时提供输入，与`-`结合可以接收来自标准输入的内容
- `grafana/k6`：镜像名称
- `run - < k6-test.js`：需要运行的命令，`- <`将后面的内容传递给run



进入数据库的方法：

1. 方法一
   1. 进入容器`docker-compose exec -it mongo bash`
   2. 在容器内执行`mongosh -u your_name -p your_password`
2. 方法二
   1. 直接在一行命令中完成`docker-compose exec -it mongo mongosh -u your_name -p your_password`



> docker compose 后台运行命令 `docker compose up -d`



### 容器命令

| 创建容器 | docker  run <imageName>             | 创建并运行容器，对象是镜像                                   |
| -------- | ----------------------------------- | ------------------------------------------------------------ |
|          | --name  <Name>                      | 命名运行后容器的名字                                         |
|          | -d                                  | 后台方式运行                                                 |
|          | -it                                 | 使用交互方式运行，进入容器查看内容。-i:保持STDIN开启，即使没有连接；-i:分配一个伪终端 |
|          | -p 主机端口:容器端口                | 指定容器的端口(小写p)                                        |
|          | -P                                  | 随机指定端口(大写P)                                          |
| 退出容器 | exit                                | 停止容器并退回主机                                           |
|          | Ctrl +  P + Q                       | 不停止容器，退回主机Ctrl+D也可以                             |
| 进入容器 | docker attach <容器id>              | 进入正在运行的容器                                           |
|          | docker exec -it <容器id>  /bin/bash | 进入容器，开启一个新的终端                                   |
| 列出容器 | docker  ps                          | 列出当前正在运行的容器                                       |
|          | -a                                  | 列出所有容器（运行的容器/未运行的容器）                      |
|          | -n=2                                | 显示最近创建的2个容器                                        |
|          | -q                                  | 只显示编号                                                   |
| 删除容器 | docker rm <容器id>                  | 不能删除正在运行的容器                                       |
|          | docker  rm -f $(docker ps -aq)      | 删除所有容器                                                 |
|          | docker  ps -a -q\|xargs docker rm   | 删除所有容器                                                 |
| 启动容器 | docker start <容器id>               | 启动停止了的容器，对象是容器                                 |
| 重启容器 | docker restart <容器id>             |                                                              |
| 停止容器 | docker stop <容器id>                |                                                              |
| 杀掉容器 | docker kill <容器id>                | 强制停止容器                                                 |

### 其他重要命令

| 查看log             | docker logs <容器id>                    |                            |
| ------------------- | --------------------------------------- | -------------------------- |
|                     | -f                                      | 会持续输出                 |
|                     | -t                                      | 显示时间戳                 |
| 查看容器进程        | docker top <容器id>                     |                            |
| 查看容器/镜像元数据 | docker inspect <容器id>                 |                            |
| 拷贝文件            | docker cp <容器id>:/path/fileName /path | 将容器内的文件拷贝到本机上 |

### 提交容器

将容器里修改的内容保存下来并生成新的镜像，避免删除容器后，数据丢失，与git类似

docker commit -a "提交作者" -m "提交的描述信息" <容器id> <新的镜像名>:[TAG]





---

## docker compose

| docker compose up -d | 启动 |
| -------------------- | ---- |
|                      |      |
|                      |      |
|                      |      |



---

## 设置镜像

```bash
sudo vim /etc/docker/daemon.json
```

填入

```tex
{
  "registry-mirrors": [
    "https://docker.1panel.live",
    "https://dockerpull.com",
    "https://hub.rat.dev"
  ]
}
```

保存后

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

查看是否生效

```bash
docker info
```

