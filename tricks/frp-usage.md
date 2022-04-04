# frp内网穿透使用说明

frp很简单，就是一个服务端，一个客户端

* 公网ip作为frp服务端，
* 内网服务器作为frp客户端

访问FRP的release页面查看对应架构的最新版下载地址，在服务器和树莓派分别下载并解压。

#### frps简单配置启动

很简单下载到的frps程序，简单配置成systemctl服务

TODO: token校验机制配置

```conf
[common]
bind_port = 7000

allow_ports = 80,443,2000-3000,3001,3003,4000-50000
```

```systemd
# /etc/systemd/system/frps.service
[Unit]
Description=Frp Server Service
After=network.target

[Service]
Type=simple
#User=nobody
User=root
Restart=on-failure
RestartSec=5s
ExecStart=/usr/bin/frps -c /etc/frp/frps.ini
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

#### frpc简单配置启动

/etc/frp/frpc.ini
```conf
[common]
server_addr = hostname
server_port = 7000

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 22345

#[http]
#type = tcp
#local_ip = 127.0.0.1
#local_port = 80
#remote_port = 80
#
#[https]
#type = tcp
#local_ip = 127.0.0.1
#local_port = 443
#remote_port = 443
#
#[adam-http]
#type = tcp
#local_ip = 127.0.0.1
#local_port = 9080
#remote_port = 9080
#
#[adam-https]
#type = tcp
#local_ip = 127.0.0.1
#local_port = 9443
#remote_port = 9443
```

```systemd
# /etc/systemd/system/frpc.service
[Unit]
Description=Frp Client Service
After=network.target

[Service]
Type=simple
User=nobody
Restart=on-failure
RestartSec=5s
ExecStart=/usr/bin/frpc -c /etc/frp/frpc.ini
ExecReload=/usr/bin/frpc reload -c /etc/frp/frpc.ini
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
```

## 参考文档

* https://chinsyo.com/2019/08/10/ssh-connect-raspberry-pi-anywhere/
