[2022年十大 VPN 协议详解【附性能对比和选择建议】](https://pandavpnpro.com/blog/zh-cn/vpn-protocol)

关键字《wireguard 协议混淆》

https://v2ex.com/t/851718
WireGuard 安裝了 2 天就被阻断了，不是说很难被识别吗？

=> WireGuard 特征很明显

https://cloud.tencent.com/developer/article/2153908
突破运营商 QoS 封锁，WireGuard 真有“一套”！

UDP over UDP 混淆

https://www.volcengine.com/theme/975118-W-7-1
wireguard混淆

使用伪装协议

#### wg工具安装

参考: https://www.cnblogs.com/milton/p/14178344.html

```
apt install wireguard-tools
=> 这个版本略低，配合我下面编译的wireguard-go有问题
```

编译安装wireguard-tools
```
git clone https://github.com/WireGuard/wireguard-tools.git
cd wireguard-tools/src
make install
```

#### wireguard-go使用

https://github.com/tailscale/wireguard-go
https://github.com/WireGuard/wireguard-go
使用 Golang 实现的 WireGuard 协议，属于用户空间(User Space)的实现，性能没有内核模块方式好，但好处就是跨平台且更简单易用。

https://lewang.dev/posts/2019-10-30-wireguard-go-setup/
WireGuard 使用简介

编译 wireguard-go
```
# 使用 GitHub 的源码镜像，速度会快一些
git clone git@github.com:wireguard/wireguard-go.git

# 在 MacOS 下交叉编译
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -v -o "wireguard-go"

# Linux 环境下直接编译

go build -v -o "wireguard-go"

cp wireguard-go /usr/sbin/
```

https://naiv.fun/Ops/53.html
安装 Wire­guard 需要分情况。如果系统的内核版本较高，那么可能已经内置了 Wire­guard，安装过程会比较简单。但对于内核版本较低的系统，安装过程可能会比较复杂，一般有两种解决方法。

自行编译安装内核模块
使用 Wireguard-go 替代

[wireguard-go的一些原理](https://juejin.cn/post/7272378529211121725)
客户端会将所有的数据包都发送到wireguard-go的虚拟网卡上吗

`wireguard-go` 主要负责实现 WireGuard 协议的逻辑，而不是直接操作网卡。它将创建一个虚拟网卡（通常称为 "tun" 设备），并将 WireGuard 数据包通过此虚拟网卡发送和接收。在实际中，这个虚拟网卡是由操作系统提供的，`wireguard-go` 只是使用它与系统网络堆栈进行交互。

https://www.liuquanhao.com/posts/OpenVZ安装WireGuard方法/
/lib/systemd/system/wg-quick@.service
systemctl start wg-quick@wg0

https://ihnic.com/index.php/archives/10/
申明使用 用户空间版本
```
export WG_I_PREFER_BUGGY_USERSPACE_TO_POLISHED_KMOD=1
wireguard-go wg
```

#### wireguard-go源码

conn/bind_std.go : send, Open

发包，xor处理bufs二维数组
```
func (s *StdNetBind) Send(bufs [][]byte, endpoint Endpoint) error {

    key := "adamxiao"
    for i := range bufs {
        for j := range bufs[i] {
            bufs[i][j] = bufs[i][j] ^ key[i % len(key)]
        }
    }

    msgs := s.getMessages()
```

收包, xor处理bufs二维数组
```
func (s *StdNetBind) receiveIP(

    // FIXME: OOB处理?
    key := "adamxiao"
    for i := 0; i < numMsgs; i++ {
        msg := &(*msgs)[i]
        for j := 0; j < msg.N; j++ {
            bufs[i][j] = bufs[i][j] ^ key[i % len(key)]
        }
    }
```

~/go/pkg/mod/golang.org/x/net@v0.15.0/ipv4/batch.go
~/go/pkg/mod/golang.org/x/net@v0.15.0/internal/socket/socket.go
https://pkg.go.dev/golang.org/x/net/internal/socket#Message
```
// A Message represents an IO message.
type Message struct {
        // When writing, the Buffers field must contain at least one
        // byte to write.
        // When reading, the Buffers field will always contain a byte
        // to read.
        Buffers [][]byte

        // OOB contains protocol-specific control or miscellaneous
        // ancillary data known as out-of-band data.
        OOB []byte

        // Addr specifies a destination address when writing.
        // It can be nil when the underlying protocol of the raw
        // connection uses connection-oriented communication.
        // After a successful read, it may contain the source address
        // on the received packet.
        Addr net.Addr

        N     int // # of bytes read or written from/to Buffers
        NN    int // # of bytes read or written from/to OOB
        Flags int // protocol-specific information on the received message
}
```

#### tailscale源码

wgengine/magicsock/magicsock.go
```
// Send implements conn.Bind.
//
// See https://pkg.go.dev/golang.zx2c4.com/wireguard/conn#Bind.Send
func (c *Conn) Send(buffs [][]byte, ep conn.Endpoint) error {
```

wgengine/userspace.go
=> journalctl日志能看到有这个日志
```
e.logf("Creating WireGuard device...")
e.wgdev = wgcfg.NewDevice(e.tundev, e.magicConn.Bind(), e.wgLogger.DeviceLogger)
```

收包修改, wgengine/magicsock/magicsock.go
```
// mkReceiveFunc creates a ReceiveFunc reading from ruc.
// The provided healthItem and metric are updated if non-nil.
func (c *Conn) mkReceiveFunc(ruc *RebindingUDPConn, healthItem *health.ReceiveFuncStats, metric *clientmetric.Metric) conn.ReceiveFunc {
```

发包修改, wgengine/magicsock/magicsock.go
```
// See https://pkg.go.dev/golang.zx2c4.com/wireguard/conn#Bind.Send
func (c *Conn) Send(buffs [][]byte, ep conn.Endpoint) error {
```

#### wireguard使用

[Set Up WireGuard VPN on Ubuntu](https://www.linode.com/docs/guides/set-up-wireguard-vpn-on-ubuntu/)

[(好)Wireguard笔记(二) 命令行操作](https://www.cnblogs.com/milton/p/15339898.html)

需要 wg 和 wg-quick 这两个工具
```
sudo apt install wireguard
wireguard-tools ?
```

配置
```
创建wg0网卡, 并设置wireguard参数

ip link add dev wg0 type wireguard
ip address add dev wg0 10.8.1.1/24
wg set wg0 listen-port 7777
wg set wg0 private-key /etc/wireguard/privatekey
wg set wg0 peer CbX0FSQ7W2LNMnozcMeTUrru6me+Q0tbbIfNlcBzPzs= allowed-ips 192.168.20.0/24,10.8.1.2/32 endpoint networkB.company.com:8888
ip link set up wg0
配置完基础参数后, 先保存设置

touch /etc/wireguard/wg0.conf
wg-quick save wg0
然后用wg-quick就可以开启/关闭wg0网卡了

wg-quick down wg0
wg-quick up wg0
```

https://www.sklinux.com/posts/devops/下一代vpn/
=> 有wg的配置文件配置示例， 以及注释

#### wg配置示例

生成密钥
```
umask 077
wg genkey | tee privatekey | wg pubkey > publickey
```

wg-quick up wg0

服务端配置 wg0.conf (其中客户端peer有多个就需要配置多个)
```
[Interface]
PrivateKey = xxx
Address = 172.99.0.1/32
PostUp   = iptables -I FORWARD -i wg0 -o eth+ -j ACCEPT; iptables -I FORWARD -i eth+ -o wg0 -j ACCEPT; iptables -t nat -I POSTROUTING -o eth+ -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -o eth+ -j ACCEPT; iptables -D FORWARD -i eth+ -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth+ -j MASQUERADE
ListenPort = 41642
MTU = 1420
FwMark = 0x7500

[Peer]
PublicKey = xxx
#PresharedKey = xxxx
AllowedIPs = 172.99.0.2/32
PersistentKeepalive = 30
```

客户端配置 client-wg0.conf
```
[Interface]
PrivateKey = xxx
Address = 172.99.0.2/32
DNS = 8.8.8.8
MTU = 1420
FwMark = 0x7500

PostUp   = ip route add 192.0.0.0/8 via x.x.x.x; ip route add 192.168.101.0/24 dev client-wg0
PostDown = ip route del 192.0.0.0/8 via x.x.x.x; ip route del 192.168.101.0/24 dev client-wg0

[Peer]
PublicKey = xxx
Endpoint = x.x.x.x:41642
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 30
```

#### 关于AllowedIPs

关键字《wireguard AllowedIPs 0.0.0.0/0设置原理》

Wireguard的AllowedIPs因为涉及服务端和客户端的允许IP范围，需要理清一下这个设置的含义

- 首先，AllowedIPs会影响当前机器的路由设置，在AllowedIPs配置的每一段IP，都会在路由表里指向这个wireguard网卡
  那么在A节点，如果你要访问B节点后面的网络，你就要把B节点后面网络的IP段，配到Peer.B下面去
- 其次，提供转发的节点，不需要关心从各个节点到来的流量要访问何处，不需要为自身转发的目标网段配置AllowedIPs
  比如A节点处于5.5.5.0/24网段，A已经提供了转发，那么A不需要在自己节点下面的Peer的AllowedIPs中配置5.5.5.0/24
  服务端和客户端的[Peer]中配置的AllowedIPs

- 无论哪一端，AllowedIPs的IP段都会加入路由表
- AllowedIPs需要包含对方节点的隧道IP
- AllowedIPs需要包含对方节点提供转发的IP网段，这将通过增加路由规则拦截本机对这些IP范围的访问流量
- **当配置的AllowedIPs为0.0.0.0/0时，会将虚拟网卡的Default Gateway设为0.0.0.0，而不是通过路由表**
```
$ ip route show table 51820
default dev wg0 scope link
```

https://www.kuangstudy.com/bbs/1599352503701753858
三、Wireguard 全局路由策略
```
$ ip rule show
0:      from all lookup local
32764:  from all lookup main suppress_prefixlength 0
32765:  not from all fwmark 0xca6c lookup 51820
32766:  from all lookup main
32767:  from all lookup default
```

[(好)Linux Wireguard和策略路由](https://telegra.ph/Linux-Wireguard和策略路由-03-17)
wg-quick 做了什么？
wg-quick 通过等价以下命令的结果完成路由所有流量的目标：
```
# wg set wg0 fwmark 51820
# ip route add default dev wg0 table 51820
# ip rule add not fwmark 51820 table 51820
# ip rule add table main suppress_prefixlength 0
```

wg-quick使用如下规则
```
iptable -t mangle -I PREROUTING -p udp -j CONNMARK --restore-mark %s
```

#### wireguard原理

https://tonybai.com/2020/03/29/hello-wireguard/

1.peer to peer vpn
点对点wireguard通信图

[(好)彻底理解 WireGuard 的路由策略](https://zhuanlan.zhihu.com/p/559789021)

## FAQ

#### ping不通

=> server端没有配置 peer 参数!
=> 配置 AllowedIPs 可以了!
```
[Peer]
PublicKey = xxx
#PresharedKey = xxxx
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 30
```

dmesg看到的日志
```
CpuUsageThread[38358]: segfault at 0 ip 00000000004136dc sp 00007fb5e19827d0 error 4 in uniagent-daemon[400000+ce000]
Code: 24 24 b8 ff ff ff ff 4d 85 e4 74 31 4c 89 e3 0f 1f 80 00 00 00 00 48 8b 7b 08 48 89 ee e8 4c c6 ff ff 85 c0 75 0a 48 8b 43 18 <66> 83 38 11 74 2e 48 8b 1b 48 85 db 75 de b8 ff ff ff ff 48 8b 4c
wireguard: wg0: Invalid handshake initiation from 192.168.101.8:48001
```

https://www.mmcloud.com/4646.html
在Linux内核中启用调试日志记录

如果使用Linux内核5.6+，可以使用以下命令启用WireGuard的调试日志记录。
```
echo module wireguard +p > /sys/kernel/debug/dynamic_debug/control
然后可以使用查看调试日志

dmesg -wH
或

journalctl -kf
```

#### wg-quick: line 32: resolvconf: command not found

https://gist.github.com/sidmulajkar/472cc9dd475ef14a598db0c64f025491
```
sudo apt install openresolv
sudo apt install resolvconf
```

或者去除DNS配置也可
