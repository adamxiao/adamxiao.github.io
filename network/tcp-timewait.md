# tcp timewait了解

关键字《tcp time wait时间》
默认2MSL (RFC定义是MSL 为 2 分钟), 内核定义TCP_TIMEWAIT_LEN = 60s

[(好)为什么 TCP 协议有 TIME_WAIT 状态](https://draveness.me/whys-the-design-tcp-time-wait/)
TIME_WAIT 仅在主动断开连接的一方出现，被动断开连接的一方会直接进入 CLOSED 状态

设计timewait状态的原因:

- 防止延迟的数据段被其他使用相同源地址、源端口、目的地址以及目的端口的 TCP 连接收到；
  => 阻止延迟数据段
- 保证 TCP 连接的远程被正确关闭，即等待被动关闭连接的一方收到 FIN 对应的 ACK 消息；
  => 保证连接关闭

总结: 如果客户端等待的时间不够长，那么使用相同端口号重新与远程建立连接时会造成以下问题：

- 因为数据段的网络传输时间不确定，所以可能会收到上一次 TCP 连接中未被收到的数据段；
- 因为客户端发出的 ACK 可能还没有被服务端接收，服务端可能还处于 LAST_ACK 状态，所以它会回复 RST 消息终止新连接的建立；

如果我们真遇到不得不处理单机上的 TIME_WAIT 状态的时候，那么可以通过以下几种方法处理：

- 1.使用 SO_LINGER 选项并设置暂存时间 l_linger 为 0，在这时如果我们关闭 TCP 连接，内核就会直接丢弃缓冲区中的全部数据并向服务端发送 RST 消息直接终止当前的连接7；
- 2.使用 net.ipv4.tcp_tw_reuse 选项，通过 TCP 的时间戳选项允许内核重用处于 TIME_WAIT 状态的 TCP 连接；
- 3.修改 net.ipv4.ip_local_port_range 选项中的可用端口范围，增加可同时存在的 TCP 连接数上限；
  需要注意的是，另一个常见的 TCP 配置项 net.ipv4.tcp_tw_recycle 已经在 Linux 4.12 中移除，所以我们不能再通过该配置解决 TIME_WAIT 设计带来的问题。

[从一次经历谈 TIME_WAIT 的那些事](https://coolshell.cn/articles/22263.html)

https://www.cnblogs.com/rexcheny/p/11143128.html
- net.ipv4.tcp_fin_timeout = 60
  这个时间不是修改2MSL的时长，主动关闭连接的一方接收到ACK之后会进入，FIN_WAIT-2状态，然后等待被动关闭一方发送FIN，这个时间是设置主动关闭的一方等待对方发送FIN的最长时长，默认是60秒。

- net.ipv4.tcp_max_tw_buckets = 6000
  同时保持TIME_WAIT套接字的最大个数，超过这个数字那么该TIME_WAIT套接字将立刻被释放并在/var/log/message日志中打印警告信息

- net.ipv4.tcp_tw_reuse
  表示开启重用。允许将一个处于TIME-WAIT状态的端口重新用于新的TCP连接，默认为0，表示关闭，其防止重复报文的原理也是时间戳，具体看后面。
  使用net.ipv4.tcp_tw_reuse和net.ipv4.tcp_tw_recycle 的前提是开启时间戳net.ipv4.tcp_timestamps = 1不过这一项默认是开启的。

https://blog.csdn.net/miqi770/article/details/125736787
net.ipv4.tcp_tw_timeout=5
阿里云linux才支持此参数
