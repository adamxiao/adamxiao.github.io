# ssh 正向端口转发

```bash
remote_ip=127.0.0.1
local_ip=127.0.0.1
ssh -N -f -L3970:${remote_ip}:3970 user_00@${local_ip} -p 36000

mysql -uusername -ppasswd -h127.0.0.1 -P3970
```

# ssh 反向隧道

```bash
ssh -p 22 -qngfNTR 22345:localhost:22 adam@${remote_ip}
```

参数解析:
* -q 安静模式
* -f 后台模式

在反向代理的时候，将绑定的端口开放到公网，而非127.0.0.1。
所以需要在sshd_config中设置GatewayPorts为yes，这样，可以直接ssh -pxxx就连接到内网了

[搭建稳定的ssh隧道](http://www.maoyingdong.com/make_ssh_tunnel_stable/)

**网络是不稳定的，连接断开时有发生。通过断线检测+断线重连+开机自启可以创建一个稳定的ssh隧道。**

网上有现成的工具autossh专门用来建立稳定的ssh连接，不过经过测试效果不好，故障率较高（可能是没有正确配置导致）。

配置ssh-link服务, /usr/lib/systemd/system/ssh-link.service
```
[Unit]
Description=ssh port forwarding service.

[Service]
Type=simple
ExecStart= /bin/sh -c 'ssh -NT -R 1122:127.0.0.1:22 用户名@服务器IP'
Restart=always
RestartSec=10
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

服务器ssh配置, 服务端检测客户端断开连接
配置/etc/ssh/sshd_config
```
ClientAliveInterval 10
ClientAliveCountMax 3
```

其中：
* ClientAliveInterval：参数表示如果服务器连续N秒没有收到来自客户端的数据包，则服务器会向客户端发送一条消息。
* ClientAliveCountMax：表示如果服务器发送了N次数据到客户端都没有收到回应时，就会认为连接已经断开，服务器会结束会话、关闭监听的端口。

上述配置表示，如果服务器连续10秒没有收到客户端的数据，就会主动发送数据给客户端。连续发送了3次数据到客户端，都没有收到回复就断开连接。这意味着，网络断开后的最长30秒内，服务器就会关闭ssh会话。


ssh客户端配置, 让客户端可以检测服务端是否存活。
配置文件/etc/ssh/ssh_config，配置以下参数：
```
ServerAliveInterval 10
ServerAliveCountMax 3
ExitOnForwardFailure yes
```
ExitOnForwardFailure表示端口转发失败时退出ssh。因为有可能服务器上要监听的端口被占用了，可能导致转发失败，这时候自动退出，systemctl才会重新执行ssh。如果不退出，systemctl就会认为ssh转发成功了，导致ssh进程存在，但是转发通道实际上没有建立。
保存之后在客户端重启ssh: `sudo systemctl restart ssh`

# ssh sock5 代理

代理端口1080
```bash
ssh -p 22345 -N -D 127.0.0.1:1080 adam@127.0.0.1
```
