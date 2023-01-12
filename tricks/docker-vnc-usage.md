## docker vnc使用

## 基本使用

```
docker run -d -p 5901:5901 -p 6901:6901 consol/centos-xfce-vnc
```

## 编译构建镜像

```
docker build -f Dockerfile.centos.xfce.vnc -t centos-vnc .
```

## ARM部署docker vnc镜像服务

1.部署安装docker
之前保留了docker的arm安装包，可以轻松安装docker。

2.构造vnc镜像
```
git clone https://github.com/adamxiao/docker-headless-vnc-container
# 修改禁止安装firefox和chrome
docker build -f Dockerfile.centos.xfce.vnc -t centos-vnc .
```

XXX: 需要arm机器上网

3.修改vnc镜像免密
```
# ./src/common/scripts/vnc_startup.sh
vncserver ... -SecurityTypes=none ...
```

4.安装firefox arm版本
```
# XXX: 更好的版本？
yum install -y firefox
```

已去除chrome桌面图片，修正firefox桌面图标

5.配置自动启动firefox做事情
XXX: 可选？？？ 做啥事请

6.修改vnc镜像背景以及logo
已改桌面背景图片

7.虚拟机定义
cpu，mem，disk确定大小？？？
TODO: cpu 70个？mem 35G？ disk 500G？
怎么弄虚拟机的内核为超过16核？（基于8.1.6处理）
手动改配置文件？

8.虚拟机配置
安装arm虚拟机;（UniKylin-3.3-6-1908-011153-aarch64.iso）
安装docker;
```
# 对应使用这个源安装docker rpm包
baseurl=http://1.1.1.1/kojifiles/repos/KY3.3-7-build/latest/aarch64/
```

默认启动docker;
导入centos-vnc镜像
默认启动70个vnc镜像容器;（做好端口映射）
其他不用管了。
```
for (( i = 0; i < 70; i++ )); do
    port=$((5900+i))
    echo "docker run -d --restart=always -p $port:5901 centos-vnc"
done
```


9.访问虚拟机里面的vnc桌面
```
iptables -t nat -A PREROUTING -p tcp -m tcp --dport 5905 -j DNAT --to-destination 192.168.84.1:5900
```

vncviewer 1.1.1.1:5

dnat端口转发
```
for (( i = 0; i < 20; i++ )); do
    port=$((5905+i))
    port2=$((6530+i))
    iptables -t nat -A PREROUTING -p tcp -m tcp --dport $port -j DNAT --to-destination 192.168.84.1:$port2
done
```

## 旧的资料

https://github.com/adamxiao/docker-headless-vnc-container

https://docs.qq.com/doc/DT0NvYWluVlFndlBT
