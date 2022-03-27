# openwrt安装使用

计划使用openwrt安装到虚拟机中，作为旁路由使用。

## openwrt镜像列表

#### sulinggg/openwrt:x86_64

参考: [在Docker 中运行 OpenWrt 旁路网关](https://mlapp.cn/376.html)
      https://hub.docker.com/r/sulinggg/openwrt

支持raspberrypi数莓派各种型号，有passwall, openclash插件, 但是v2ray配置都感觉没有生效
ImmortalWrt, 页面优化过, 效果可以

#### hoisum/openwrt_x86_64:r22.3.13_20220318

参考: [X86-64 OpenWrt Docker镜像简易版](https://www.right.com.cn/forum/thread-7045474-1-1.html)

有几个v2ray插件：
passwall, openclash, shadowsocksR plus+
同样没有配置成功v2ray科学上网

#### crazygit/lean-openwrt-x86-64

参考: https://github.com/crazygit/family-media-center
跟上面的openwrt几乎一样的，就是没有科学上网插件

#### crazygit/openwrt-x86-64

参考: https://github.com/crazygit/openwrt-x86-64 
最原始的openwrt镜像了，没有一个插件，没有密码

## openwrt docker镜像使用

参考 https://github.com/crazygit/family-media-center/blob/master/docker-compose.openwrt.yml

=> 目前这个镜像感觉最好
```bash
docker run --name openwrt -d --privileged --restart always \
  --network openwrt-LAN --ip 192.168.0.200 \
  crazygit/lean-openwrt-x86-64
```

docker-compose.yml
```yaml
version: '3.7'

services:
  openwrt:
    image: crazygit/lean-openwrt-x86-64
    restart: always
    privileged: true
    volumes:
      - ./etc/config/network:/etc/config/network
      - ./etc/rc.local:/etc/rc.local
    networks:
      macvlan:
        ipv4_address: 192.168.0.200

networks:
  macvlan:
    external:
      name: openwrt-LAN

#networks:
#  macvlan:
#    driver: macvlan
#    driver_opts:
#      # 宿主机网卡
#      parent: enp3s0
#    ipam:
#      config:
#        - subnet: 192.168.0.0/24
#          gateway: 192.168.0.1
```

./etc/config/network
```
config interface 'lan'
        #option type 'bridge'
        option ifname 'eth0'
        option proto 'static'
        # 分配给openwrt系统的IP地址
        option ipaddr '192.168.0.200'
        # 子网掩码
        option netmask '255.255.255.0'
        # 主路由的网关
        option gateway '192.168.0.1'
        # DNS
        option dns '192.168.0.1'
        # 广播地址
        option broadcast '192.168.0.255'
        #option ip6assign '60'
```

./etc/rc.local
```bash
# Put your custom commands here that should be executed once
# the system init finished. By default this file does nothing.

# 修复DNS总是被设置为127.0.0.11的问题,使用本机的dnsmasq
# https://github.com/coolsnowwolf/lede/issues/4110

cat > /etc/resolv.conf <<EOF
search lan
nameserver 127.0.0.1
options ndots:0
EOF


exit 0
```

## openwrt docker镜像使用

参考  FIXME: 目前只有arm/v7架构的镜像
=> 不行，毕竟是arm/v7镜像，没能验证
```bash
docker run --name openwrt -d --privileged --restart always \
  --network openwrt-LAN --ip 192.168.0.200 \
  registry.cn-shanghai.aliyuncs.com/suling/openwrt:latest /sbin/init
```


## openwrt docker镜像使用

发现有openwrt的docker镜像可以使用, 先使用一下。

#### 直接使用

参考: https://github.com/crazygit/openwrt-x86-64

```bash
docker run --rm crazygit/openwrt-x86-64 cat /etc/banner
```

#### 镜像使用配置

#### 1.为docker创建macvlan模式的虚拟网络

子网--subnet和网关--gateway，以及parent=enp3s0网卡名称根据实际情况做调整

```bash
docker network create -d macvlan \
  --subnet=192.168.0.0/24 \
  --gateway=192.168.0.1 \
  -o parent=enp3s0 \
  openwrt-LAN

# 查看创建的虚拟网络
docker network ls |grep openwrt-LAN
21dcddacc389        openwrt-LAN         macvlan             local
```

#### 2. 启动容器

指定了容器的ip地址
```bash
# --network使用第4步创建的虚拟网络
docker run --name openwrt -d --privileged --restart always \
  --network openwrt-LAN --ip 192.168.0.200 \
  crazygit/openwrt-x86-64

# 查看启动的容器
docker ps -a
```

#### 3. 进入容器，修改网络配置文件并重启网络

```bash
docker exec -it openwrt /bin/sh
vi /etc/config/network
```

编辑lan口的配置如下，有些参数默认的文件里可能没有，按照下面的格式添加上即可
```conf
config interface 'lan'
        option type 'bridge'
        option ifname 'eth0'
        option proto 'static'
        option ipaddr '192.168.0.200'
        option netmask '255.255.255.0'
        option gateway '192.168.0.1'
        option dns '192.168.0.1'
        option broadcast '192.168.0.255'
        option ip6assign '60'
```

上面的参数根据自身的情况调整

* proto设置使用静态分配IP地址的方式static
* ipaddr为OpenWrt系统分配的静态IP，这里我分配的是192.168.2.126(注意: 这个IP地址不要与你本地网络已有的IP地址冲突)
* netmask为子网掩码255.255.255.0
* gateway为路由器(硬路由)的网关，通常就是你访问路由器的IP地址，这里我是192.168.2.1
* dns为DNS服务器的地址，可以是运营商的地址，比如114.114.114.114,这里我直接用的路由器的地址192.168.2.1
* broadcast为广播地址192.168.2.255

重启网络
```
/etc/init.d/network restart
```

#### 4. 验收成果

使用配置openwrt的ip地址登录系统，帐号root，密码空。
![](https://github.com/crazygit/openwrt-x86-64/raw/master/screenshots/openwrt_login.png)

剩下的就是openWrt系统的常规使用和配置，这里就不再详述了

#### 99. 宿主机配置macvlan网络

宿主机接口ip地址在物理口上，无法访问openwrt容器的网络，配置成macvlan网络就能访问了。

```bash
#根据实际情况修改如下配置
iface="enp3s0"
ipaddr="192.168.0.100/24"
gateway="192.168.0.1"

sudo ifconfig $iface 0
sudo ip link add link $iface name macv1 type macvlan mode bridge
sudo ip addr add $ipaddr brd + dev macv1
sudo ip link set macv1 up
sudo ip route del default
sudo ip route add default via $gateway dev macv1

# (可选)设置宿主机的dns, 手动修改/etc/resolv.conf
```

## openwrt配置旁路网关

主要就是配置lan口禁用bridge，以及nat转换?

## openwrt配置v2ray代理

#### openclash科学上网

使用openclash配置, 参考youtube视频 [OpenClash使用教程，支持V2ray/SSR/Trojan/vmess节点，OpenWrt软路由翻墙教程， Clash设置方法【新手教学】](https://www.youtube.com/watch?v=Cr7mE5aOlYo&ab_channel=%E7%A7%91%E6%8A%80%E5%88%86%E4%BA%AB)

主要问题就是语法检查失败!!!
![](2022-03-27-17-03-56.png)

还有依赖内核模块? 是clash_tun吗?

错误：【Dev】内核最新版本检测失败，请稍后再试...

[openclash的依赖](https://github.com/vernesong/OpenClash)可能如下:

* iptables-mod-tproxy
* iptables-mod-extra
* kmod-tun(TUN模式)
* luci-compat(Luci-19.07)
* ip6tables-mod-nat(ipv6)
* ...

参考: https://opssh.cn/luyou/80.html

最后啰嗦一句，OpenClash 小猫咪网络代理插件对新手是不太友好的，折腾起来也非常复杂，建议使用 SSR Plus+ 或 PassWall，相关说明请查看《SSRPlus、PassWall、OpenClash插件对比》。

#### passwall科学上网

发现导入的v2ray节点没有配置AlterID, 导致无法科学上网
更新的vless协议，不需要alterid (发现shadowsocksR plus+的vmess协议也没有alterID)

## openwrt安装到x86虚拟机中


https://netflixcn.com/miji/46.html
使用这个固件，安装到虚拟机中，配置passwall上网，实现了科学上网！！！
openwrt-x86-64-squashfs-combined-D201231-Mask.img.gz

TODO: 将这个做成一个docker镜像来使用？

参考 [OpenWrt x86系统升级最佳实践](https://acris.me/2021/07/09/OpenWrt-x86-System-Upgrade-Best-Practices/)

```bash
dd if=/path/to/openwrt-xxx.img of=/dev/sdX
```

[Openwrt x86安装教程](https://w2x.me/2019/03/13/openwrt-x86%E5%AE%89%E8%A3%85%E6%95%99%E7%A8%8B/)

[x86-64 设备安装配置 OpenWRT](https://shenyu.me/2021/02/26/x86-64-install-openwrt.html)


## 其他openwrt固件

* [最新编译OpenWrt X86-64纯净版软路由固件镜像下载 LEDE精简版-多功能版-旁路由固件](https://mxcheats.com/3.html)
  => 有科学上网，旁路由！！！
