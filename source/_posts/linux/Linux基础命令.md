---
title: 【Linux】Linux基础命令
date: 2023-08-22 10:02:06
tags: Linux
---

### 防火墙 

#### 基础命令

| 基础命令                               | 效果                   |
| -------------------------------------- | ---------------------- |
| `systemctl start firewalld.service`    | 开启防火墙             |
| `systemctl status firewalld.service`   | 查看防火墙状态         |
| `systemctl stop firewalld.service`     | 关闭防火墙             |
| `systemctl enable firewalld.service`   | 开启时自启             |
| `systemctl disable firewall.service`   | 关闭开机自启           |
| `systemctl is-enable firewall.service` | 查看服务是否开机自启   |
| `systemctl --failed`                   | 查看启动失败的服务列表 |

#### 配置防火墙

| 命令                                                       | 效果                                                    |
| ---------------------------------------------------------- | ------------------------------------------------------- |
| `firewall-cmd --zone=public --list-ports`                  | 查看开放的端口                                          |
| `firewall-cmd --reload`                                    | 重新载入防火墙                                          |
| `firewall-cmd --zone=public --add-port=80/tcp --permanent` | 开放80端口，`--premanent`表示永久开放，重启后也依然开放 |

每次在配置完防火墙之后需使用`firewall-cmd --reload`更新配置
