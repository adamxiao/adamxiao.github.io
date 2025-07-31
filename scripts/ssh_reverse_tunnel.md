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

#### ssh random service

/etc/systemd/system/random-ssh-link.service
```
[Unit]
Description=Check API and Control ServerA Service
After=network.target

[Service]
Type=simple
User=root
#WorkingDirectory=/opt
ExecStart=/usr/bin/python3 /usr/bin/random-ssh-link.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

random-ssh-link.py
```
#!/usr/bin/env python3

#import requests
import socket
import subprocess
import random
import time

# 服务器的HTTP接口URL
API_URL = 'http://x.x.x.x:8080/dir1/func1'

#def check_api():
#    try:
#        response = requests.get(API_URL)
#        print(response)
#        if response.status_code == 200 and response.text.strip().lower() == 'true':
#            return True
#        else:
#            return False
#    except requests.RequestException as e:
#        #print(f"Error: {e}")
#        return False

# 目标服务器信息
TARGET_HOST = 'x.x.x.x'
TARGET_PORT = 8080  # 替换为要检查的端口号

def check_port_open(host, port):
    """检查给定的主机和端口是否开放"""
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            return True
    except (socket.timeout, socket.error):
        return False

def control_service(action):
    # 根据你的操作系统和服务名修改这条命令。
    # 这里假设是Linux系统并且服务名为ssh1。
    command = f'systemctl {action} ssh1'
    try:
        result = subprocess.run(command, shell=True, check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f'Service action "{action}" completed with output: {result.stdout.decode()}')
    except subprocess.CalledProcessError as e:
        print(f'Failed to {action} service: {e.stderr.decode()}')

def main():
    while True:
        #if check_api():
        if check_port_open(TARGET_HOST, TARGET_PORT):
            control_service('start')
        else:
            control_service('stop')

        # 随机选择5到10分钟之间的等待时间
        wait_time = random.randint(5, 7) * 60  # 转换为秒
        print(f"Waiting for {wait_time / 60} minutes before next check.")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()
```

# ssh sock5 代理

代理端口1080
```bash
ssh -p 22345 -N -D 127.0.0.1:1080 adam@127.0.0.1
```

## FAQ

#### channel 1: open failed: administratively prohibited: open failed

sshd对端日志
refused streamlocal port forward: originator  port 0, target //var/run/ksvd//336b-clone.socket
发现use_privsep=0, 所以无法转发unix套接字
```
static Channel *
server_request_direct_streamlocal(void)
{
...
        /* XXX fine grained permissions */
        if ((options.allow_streamlocal_forwarding & FORWARD_LOCAL) != 0 &&
            !no_port_forwarding_flag && !options.disable_forwarding &&
            use_privsep) {
                c = channel_connect_to_path(target,
                    "direct-streamlocal@openssh.com", "direct-streamlocal");
        } else {
                logit("refused streamlocal port forward: "
                    "originator %s port %d, target %s",
                    originator, originator_port, target);
        }
```

UsePrivilegeSeparation yes
rooty用户useprivi=0代码中写死的,换个kylin普通用户即可?
```
static void
privsep_postauth(Authctxt *authctxt)
{
#ifdef DISABLE_FD_PASSING
    if (1) {
#else
    if (authctxt->pw->pw_uid == 0) {
#endif
        /* File descriptor passing is broken or root login */
        use_privsep = 0;
        goto skip;
    }
```

AllowStreamLocalForwarding 配置为all，发现一直都是yes, 有问题
但是改为local就可以？？？ => 没用, 其实all就是yes?

https://www.nixcraft.com/t/channel-1-open-failed-administratively-prohibited-open-failed-with-ssh-tunneling/3773/2
```
2. How to find current settings
Run the following command on your Linux or Unix SSHD server:

sudo sshd -T | grep -Ei 'TCPKeepAlive|AllowTCPForwarding|PermitOpen'
Correct values:

tcpkeepalive yes
allowtcpforwarding yes
permitopen any
```
