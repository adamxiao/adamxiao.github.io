# tailscale使用

Tailscale 是什么

安装tailscale

https://tailscale.com/download/linux

有rpm包安装

ubuntu 20.04
```
Add Tailscale’s package signing key and repository:

curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list

Install Tailscale:

sudo apt-get update
sudo apt-get install tailscale
Connect your machine to your Tailscale network and authenticate in your browser:

sudo tailscale up
You’re connected! You can find your Tailscale IPv4 address by running:

tailscale ip -4
```

使用
```
tailscale up --login-server=http://<HEADSCALE_PUB_IP>:8080 --accept-routes=true --accept-dns=false --advertise-routes=192.168.100.0/24 --reset

tailscale up --advertise-routes=10.30.0.0/16,10.90.0.0/16 --reset
Warning: IPv6 forwarding is disabled.
Subnet routes and exit nodes may not work correctly.
See https://tailscale.com/s/ip-forwarding

tailscale up --accept-routes=true --reset
```

https://tailscale.com/kb/1019/subnets/?tab=linux

可以查看这个表, 发现获取到路由了
```
ip route show table 52
```

## headscale使用

容器镜像使用, 关键字《headscale 容器镜像使用》

https://github.com/iFargle/headscale-webui/issues/79

```
version: '3.6'
services:
    headscale:
        container_name: headscale
        restart: always
        volumes:
            - ./config:/etc/headscale/
            - ./data:/var/lib/headscale
        ports:
            - '4050:8080' #自己喜欢映射到哪个端口就用哪个端口，对应的防火墙请放行
            - '9090:9090'
            - '3478:3478/udp'
        command: 'headscale serve'
        networks:
            headscale:
        image: 'headscale/headscale:latest'
        cap_add:
            - NET_ADMIN
            - SYS_MODULE
        sysctls:
            - net.ipv4.ip_forward=1

#声明已有网络
networks: 
    headscale: 
        name: headscale
        external: false
```

https://icloudnative.io/posts/how-to-set-up-or-migrate-headscale/
理论上来说只要你的 Headscale 服务可以暴露到公网出口就行，但最好不要有 NAT，所以推荐将 Headscale 部署在有公网 IP 的云主机上。

创建 Headscale 配置文件：
```
wget https://github.com/juanfont/headscale/raw/main/config-example.yaml -O /etc/headscale/config.yaml
```

- 修改配置文件，将 server_url 改为公网 IP 或域名。如果是国内服务器，域名必须要备案。我的域名无法备案，所以我就直接用公网 IP 了。
- 如果暂时用不到 DNS 功能，可以先将 magic_dns 设为 false。
- server_url 设置为 http://<PUBLIC_IP>:8080，将 <PUBLIC_IP> 替换为公网 IP 或者域名。
- 可自定义私有网段，也可同时开启 IPv4 和 IPv6：

#### tailscale接入headscale

```
# 将 <HEADSCALE_PUB_IP> 换成你的 Headscale 公网 IP 或域名
$ tailscale up --login-server=http://<HEADSCALE_PUB_IP>:8080 --accept-routes=true --accept-dns=false
```
执行完上面的命令后，会出现下面的信息：
```
To authenticate, visit:

http://xxxxxx:8080/register?key=905cf165204800247fbd33989dbc22be95c987286c45aac3033937041150d846
```

在浏览器中打开该链接，就会出现如下的界面：
=> 最终使用headscale命令通过认证

```
headscale nodes register --user USERNAME --key nodekey:8a25df956393caf4b4b2b11d59a669a8070e45ce39150994c0672d26a1a57852
```

#### xxx

Tailscale 中有一个概念叫 tailnet，你可以理解成租户，租户与租户之间是相互隔离的，具体看参考 Tailscale 的官方文档： What is a tailnet。Headscale 也有类似的实现叫 namespace，即命名空间。我们需要先创建一个 namespace，以便后续客户端接入，例如：

```
headscale namespaces create default
```
查看命名空间
headscale namespaces list

#### headscale命令使用

headscale nodes list
headscale routes list -i 6

开启路由
```
headscale routes enable -i 6 -r "192.168.100.0/24"
headscale routes enable -i 6 -a
```

## 流量混淆

关键字《wireguard流量识别》

求求你们别吹Wireguard了，不适合用来翻墙真的。
加密和能不能被识别是两回事，主流VPN主要实现方向是加密，ss之类的翻墙软件要实现没有特征不被识别。
加密的意思是：中间人不知道流量的具体内容，但知道你在用VPN
没有特征是：中间人不知道你这个流量是干嘛的，不知道你是在翻墙
Wireguard 属于前者

[安全上网的迷思](https://wingu.se/2021/07/29/networking.html)

[隐藏UDP流量 — Wireguard](https://medium.com/@hunter.xue/隐藏udp流量-wireguard-950f911056cf)

[使用 Phantun 将 WireGuard 的 UDP 流量伪装成 TCP](https://icloudnative.io/posts/wireguard-over-tcp-using-phantun/)

[wireguard混淆](https://www.volcengine.com/theme/975118-W-7-1)

混淆的原理

混淆就是通过对WireGuard数据包的内容进行一些变换，使其看起来与正常的数据包一样，而不会被识别为VPN流量。混淆的关键在于以下两个方面：

- 使用伪装协议
伪装协议是指将WireGuard数据包通过伪装成其他协议的数据包来规避网络审查。现在比较常用的伪装协议有TCP、HTTP、TLS等。例如，将WireGuard数据包封装在TLS的加密层中，就能使其看起来像是HTTPS流量，从而避免被审查系统检测到。

- 产生随机变化
由于网络审查系统不断更新，会知道大量的伪装协议，因此为了进一步破解WireGuard混淆，需要产生随机变化。这可以通过为加密密钥提供随机性、改变随机端口和伪装协议等方式来实现。



[(好)WireGuard Over VLESS——一个更稳定的三层隧道](https://icloudnative.io/posts/wireguard-over-tcp-using-phantun://www.40huo.cn/blog/wireguard-over-vless.html)

https://machbbs.com/v2ex/515176
WireGuard 不是为了反审查而提出的协议（它解决的问题是简化组网），要防识别建议套一层 udp2raw 之类的混淆
我搭在 oracle 云上的 wg 也是被封，用 udp2raw 模拟成 tcp 就解决了。

https://lists.zx2c4.com/pipermail/wireguard/2018-September/003289.html
Let's talk about obfuscation again

https://www.kanshan.co/archives/22.html
如果有定制化的需求，而且有一定的专业能力和动手能力，可以使用Wireguard，灵活性会更高，且Wireguard完全开源
对于网络组网等不太熟悉的新手，建议使用Tailscale和Zerotier。

https://hellodk.cn/post/1130
- frp，这个非常有名了，简单易用高效，我就在用
- ngrok，同楼上，但是传播广度和用户应该没有 frp 多
- 花生壳一类
- 如果你的家宽有动态 public IP，那可以配置 ddns 实现需求
- public IP + OpenWrt + firewall port forwarding + nginx proxy_pass
- OpenVPN 等 VPN 方案（还有 PPTP L2TP 等）
- WireGuard，同楼上，属于 VPN 方案，但是协议更新，更适合使用
- tailscale zerotier 等组网方案
- todesk，向日葵等方案
- other...

#### derp中继服务器

关键字《自建 derp 服务器》

https://blog.aflybird.cn/2023/05/tailscale-derp/

https://icloudnative.io/posts/custom-derp-servers/

[自建DERP服务器](https://lxnchan.cn/ubuntu-derp.html)

/etc/systemd/system/derp.service
```
[Unit]
Description=Tailscale DERP Server
After=network.target

[Service]
Restart=always
RestartSec=5
ExecStart=/root/go/bin/derper -c=/root/derper.conf -a ":<port>" -hostname "<domain>" --stun

[Install]
WantedBy=multi-user.target
```

开启对应防火墙端口（默认）

- STUN：UDP: 3478

- DERP: TCP: 443

http://junyao.tech/posts/18297f50.html
Tailscale 使用的算法很有趣: __所有客户端之间的连接都是先选择 DERP 模式（中继模式），这意味着连接立即就能建立（优先级最低但 100% 能成功的模式），用户不用任何等待。然后开始并行地进行路径发现，通常几秒钟之后，我们就能发现一条更优路径，然后将现有连接透明升级（upgrade）过去，变成点对点连接（直连）__。

## 参考资料

- [Tailscale 基础教程：Headscale 的部署方法和使用教程](https://icloudnative.io/posts/how-to-set-up-or-migrate-headscale/)

- [一文带你理解 WireGuard 路由策略](https://blog.csdn.net/easylife206/article/details/127699058)
  它不会扰乱你的主路由表，而是通过规则匹配新创建的路由表。断开连接时只需删除这两条路由规则，默认路由就会被重新激活

- https://cshihong.github.io/2020/10/11/WireGuard基本原理/

## FAQ

#### Cannot register machine: failed to find user in register machine from auth callback, User not found

注册的那条命令行里USERNAME改default就可以了
