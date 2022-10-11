# socat使用

关键字《socat unix socket to tcp》
=> 很多资料

https://serverfault.com/questions/517906/how-to-expose-a-unix-domain-socket-directly-over-tcp
```
socat TCP-LISTEN:12345,reuseaddr,fork,su=haproxy UNIX-CLIENT:/var/program/program.cmd
```

exec socat stdin,raw,echo=0,escape=0x11 "unix-connect:${SOCKET}"

socat UNIX-CLIENT:/tmp/336b.socket UNIX-CLIENT:/tmp/336b-clone.socket

#### 操作Unix套接字

Unix 套接字是非常常见的本地通讯方式，但是能够操作这类套接字的工具命令不多， socat 是其中一个。 下面这个例子，通过 HAProxy 的 Unix 套接字，获取其运行信息，包含 PID 、启动时间等：
```
echo "show info" | socat unix-connect:/var/tmp/haproxy stdio
```


https://unix.stackexchange.com/questions/420543/building-a-unix-socket-bridge-via-tcp
=> 非常适合我的场景
ssh -L /path/to/client.sock:/path/to/server.sock serverhost

查询unix套接字
```
netstat -ap --unix
```

## xx

## 参考文档

[socat by example](https://www.bitkistl.com/2016/03/socat-by-example.html)

https://www.361shipin.com/blog/1509326899963232256

```
1. 听tcp 12345端口
# nc -l 127.0.0.1 12345
# socat tcp-listen:12345 -
2. 向远处tcp 12345端口发点字
# echo “test” | nc 127.0.0.1 12345
# echo “test” | socat - tcp-connect:127.0.0.1:12345
3. 听udp 23456端口
# nc -u -l 127.0.0.1 23456
# socat udp-listen:23456 -
4. 向远处udp 23456端口发点字
# echo “test” | nc -u 127.0.0.1 23456
# echo “test” | socat - udp-connect:127.0.0.1:23456
5. 听unix socket /tmp/unix.socket
# nc -U -l /tmp/unix.socket
netcat没有-U选项
# socat unix-listen:/tmp/unix.socket -
6. 向本地unix socket /tmp/unix.socket发点字
# echo “test” | nc -U /tmp/unix.socket
netcat没有-U选项
# echo “test” | socat - unix-connect:/tmp/unix.sock
7. 听本地unix datagram socket /tmp/unix.dg.sock
nc110搞不定, netcat也搞不定
# socat unix-recvfrom:/tmp/unix.dg.sock -
8. 向本地unix datagram socket /dev/log发点字
nc110搞不定, netcat也搞不定
# echo “test” | socat - unix-sendto:/tmp/unix.dg.sock
```

socat unix-listen:/tmp/336b-clone.socket -

ssh -o StreamLocalBindUnlink=yes -N -L /tmp/336b-clone-proxy.socket:/tmp/336b-clone.socket kylin-ksvd@node6

socat -d -d stdin,raw,echo=0,escape=0x11 "unix-connect:/tmp/336b-clone-proxy.socket"

[socat：Linux/Unix的下TCP端口转发器](https://fasionchan.com/network/translations/socat-linux-unix-tcp-port-forwarding/)
不用 防火墙 ( firewall )软件， Linux/Unix 系统能否实现 端口转发 ( port-forwarding )呢？ socat ( SOcket CAT )是一个多用途双向数据转接工具，如何在 Linux 系统中安装呢？

socat 功能跟 NetCat 一样，但更安全(支持 chroot )，兼容多种协议， 支持操作 文件 ( file )、 管道 ( pipe )、 设备 ( device )、 TCP 套接字、 Unix 套接字、 SOCKS 客户端、 CONNECT 代理以及 SSL 等等。

本文译自：[socat: Linux/UNIX TCP Port Forwarder](https://www.cyberciti.biz/faq/linux-unix-tcp-port-forwarding/)

典型用途
* TCP 端口转发 ( port forwarding )；
* 外部套接字嗅探；
* 攻击弱防火墙(安全测试)；
* Unix 套接字的 shell 操作接口；
* IPv6 转接；
* 安全测试和研究；
