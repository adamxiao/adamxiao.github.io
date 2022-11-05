# journalctl日志查看方法

## 基本使用

4、查看系统本次启动的日志
```
journalctl -b
或者
journalctl -b -0
或者
journalctl  -b  0
```

5、查看上一次启动的日志
```
需更改设置/etc/systemd/journald.conf文件，以开启永久存储。
[root@CENTOS57 proc]# journalctl -b -1
```

7、按服务过滤消息日志
```
#查看httpd服务的日志信息
[root@centos7 ~]# journalctl -u httpd.service 
```

## journal 日志清理

可能改时间，导致时间错乱，journal日志查看也比较难

https://www.cnblogs.com/jiuchongxiao/p/9222953.html

如果要手工删除日志文件，则在删除前需要先轮转一次journal日志
```
systemctl kill --kill-who=main --signal=SIGUSR2 systemd-journald.service
```

## FAQ

#### keepalived没有journal日志没有输出

导火索是发现keepalived没有journal日志输出

关键字`/dev/log connection refused`
https://unix.stackexchange.com/questions/317064/how-do-i-restore-dev-log-in-systemdrsyslog-host
=> 最终这个居然解决了我的问题?
```
systemctl restart systemd-journald.socket && systemctl restart rsyslog
```

keepalived父进程打印syslog日志的strace日志
```
29639 19:23:55.339442 socket(AF_LOCAL, SOCK_DGRAM|SOCK_CLOEXEC, 0) = 3 <0.000013>
29639 19:23:55.339468 connect(3, {sa_family=AF_LOCAL, sun_path="/dev/log"}, 110) = 0 <0.000013>                                                29639 19:23:55.339495 sendto(3, "<30>Nov  1 19:23:55 Keepalived[29639]: Starting Keepalived v1.3.5 (03/19,2017), git commit v1.3.5-6-g6fa32f2", 108, MSG_NOSIGNAL, NULL, 0) = 108 <0.000016> 
```

查看syslog服务情况
```
$systemctl status rsyslog
● rsyslog.service - System Logging Service
   Loaded: loaded (/usr/lib/systemd/system/rsyslog.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2022-10-24 15:53:14 CST; 1 weeks 1 days ago
     Docs: man:rsyslogd(8)
           http://www.rsyslog.com/doc/
 Main PID: 21874 (rsyslogd)
    Tasks: 3
   Memory: 195.9M
   CGroup: /system.slice/rsyslog.service
           └─21874 /usr/sbin/rsyslogd -n

rsyslogd[21874]: imjournal: journal reloaded... [v8.24.0-34.ky3.kb2 try http://www.rsyslog.com/e/0 ]
rsyslogd[21874]: sd_journal_get_cursor() failed: 'Cannot assign requested address'  [v8.24.0-34.ky3.kb2]
rsyslogd[21874]: imjournal: journal reloaded... [v8.24.0-34.ky3.kb2 try http://www.rsyslog.com/e/0 ]
rsyslogd[21874]: imjournal: journal reloaded... [v8.24.0-34.ky3.kb2 try http://www.rsyslog.com/e/0 ]
rsyslogd[21874]: sd_journal_get_cursor() failed: 'Cannot assign requested address'  [v8.24.0-34.ky3.kb2]
rsyslogd[21874]: imjournal: journal reloaded... [v8.24.0-34.ky3.kb2 try http://www.rsyslog.com/e/0 ]
rsyslogd[21874]: imjournal: journal reloaded... [v8.24.0-34.ky3.kb2 try http://www.rsyslog.com/e/0 ]
rsyslogd[21874]: sd_journal_get_cursor() failed: 'Cannot assign requested address'  [v8.24.0-34.ky3.kb2]
rsyslogd[21874]: imjournal: journal reloaded... [v8.24.0-34.ky3.kb2 try http://www.rsyslog.com/e/0 ]
rsyslogd[21874]: imjournal: journal reloaded... [v8.24.0-34.ky3.kb2 try http://www.rsyslog.com/e/0 ]
```

https://unix.stackexchange.com/questions/464361/examining-dev-log
手动测试往/dev/log产生日志文件
```
echo 'This is a test!!' | nc -u -U /dev/log 
或者使用logger命令
logger Hello
```

https://serverfault.com/questions/1069377/what-happens-to-logs-generated-by-logger-if-there-is-no-logging-daemon-installed
使用fuser查看socket被哪些进程使用?
```
[ssh_10.60.5.113] root@node7: ~$fuser -v /dev/log
                     USER        PID ACCESS COMMAND
/dev/log:            root          1 F.... systemd
                     root      11219 F.... systemd-journal
可以查看哪个进程占用文件
fuser -k
```

https://www.cnblogs.com/xybaby/p/6596431.html
日志从应用程序到最终的日志文件（或者远程服务器）的流程如下：

app -> systemd -> rsyslogd -> local or remote file
![](../imgs/1089769-20170323163540080-1733313578.png)

感觉就是journal日志满了，然后无法输出journal日志，应该跟coreos一样
```
$systemctl status -l systemd-journald
● systemd-journald.service - Journal Service
   Loaded: loaded (/usr/lib/systemd/system/systemd-journald.service; static; vendor preset: disabled)
   Active: active (running) since Mon 2022-10-24 15:53:14 CST; 1 weeks 1 days ago
     Docs: man:systemd-journald.service(8)
           man:journald.conf(5)
 Main PID: 11219 (systemd-journal)
   Status: "Processing requests..."
    Tasks: 1
   Memory: 1.1G
   CGroup: /system.slice/systemd-journald.service
           └─11219 /usr/lib/systemd/systemd-journald

systemd-journal[11219]: Runtime journal is using 8.0M (max allowed 4.0G, trying to leave 4.0G free of 188.2G available → current limit 4.0G).
systemd-journal[11219]: Journal started
systemd-journal[11219]: Permanent journal is using 3.9G (max allowed 4.0G, trying to leave 4.0G free of 16.6G available → current limit 4.0G).
systemd-journal[11219]: Time spent on flushing to /var is 67.275ms for 1810 entries.
```

strace systemd-journal, 能收到日志recvmsg, this is a test
```
recvmsg(5, {msg_name={sa_family=AF_UNIX, sun_path="/tmp/ncat.Oy2OIj"}, msg_namelen=128->19, msg_iov=[{iov_base="This is a test!!\n", iov_len=24575}], msg_iovlen=1, msg_control=[{cmsg_len=32, cmsg_level=SOL_SOCKET, cmsg_type=SCM_TIMESTAMP, cmsg_data={tv_sec=1667304455, tv_usec=730106}}, {cmsg_len=28, cmsg_level=SOL_SOCKET, cmsg_type=SCM_CREDENTIALS, cmsg_data={pid=19261, uid=0, gid=0}}, {cmsg_len=70, cmsg_level=SOL_SOCKET, cmsg_type=SCM_SECURITY, cmsg_data="unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023\0"}], msg_controllen=136, msg_flags=MSG_CMSG_CLOEXEC}, MSG_DONTWAIT|MSG_CMSG_CLOEXEC) = 17
sendmsg(5, {msg_name={sa_family=AF_UNIX, sun_path="/run/systemd/journal/syslog"}, msg_namelen=29, msg_iov=[{iov_base="This is a test!!\n", iov_len=17}], msg_iovlen=1, msg_control=[{cmsg_len=28, cmsg_level=SOL_SOCKET, cmsg_type=SCM_CREDENTIALS, cmsg_data={pid=19261, uid=0, gid=0}}], msg_controllen=28, msg_flags=0}, MSG_NOSIGNAL) = -1 ENOENT (No such file or directory)
```

epoll发现有数据可以读
```
epoll_wait(7, [{EPOLLIN, {u32=3262219328, u64=94054456067136}}], 23, -1) = 1
clock_gettime(CLOCK_BOOTTIME, {tv_sec=558548, tv_nsec=277147405}) = 0
epoll_ctl(7, EPOLL_CTL_ADD, 11, {EPOLLOUT, {u32=3262223232, u64=94054456071040}}) = 0
timerfd_settime(12, TFD_TIMER_ABSTIME, {it_interval={tv_sec=0, tv_nsec=0}, it_value={tv_sec=558645, tv_nsec=400508000}}, NULL) = 0
epoll_wait(7, [{EPOLLIN, {u32=3262219328, u64=94054456067136}}, {EPOLLOUT, {u32=3262223232, u64=94054456071040}}], 23, 0) = 2
clock_gettime(CLOCK_BOOTTIME, {tv_sec=558548, tv_nsec=277646804}) = 0
sendto(11, "WATCHDOG=1", 10, MSG_DONTWAIT, NULL, 0) = 10
epoll_ctl(7, EPOLL_CTL_DEL, 11, NULL)   = 0
epoll_wait(7, [{EPOLLIN, {u32=3262219328, u64=94054456067136}}], 23, 0) = 1
clock_gettime(CLOCK_BOOTTIME, {tv_sec=558548, tv_nsec=278061545}) = 0
ioctl(5, FIONREAD, [17])                = 0
recvmsg(5, {msg_name={sa_family=AF_UNIX, sun_path="/tmp/ncat.ZKBuYk"}, msg_namelen=128->19, msg_iov=[{iov_base="This is a test!!\n", iov_len=24575}], msg_iovlen=1, msg_control=[{cmsg_len=32, cmsg_level=SOL_SOCKET, cmsg_type=SCM_TIMESTAMP, cmsg_data={tv_sec=1667349633, tv_usec=843432}}, {cmsg_len=28, cmsg_level=SOL_SOCKET, cmsg_type=SCM_CREDENTIALS, cmsg_data={pid=32408, uid=0, gid=0}}, {cmsg_len=70, cmsg_level=SOL_SOCKET, cmsg_type=SCM_SECURITY, cmsg_data="unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023\0"}], msg_controllen=136, msg_flags=MSG_CMSG_CLOEXEC}, MSG_DONTWAIT|MSG_CMSG_CLOEXEC) = 17
sendmsg(5, {msg_name={sa_family=AF_UNIX, sun_path="/run/systemd/journal/syslog"}, msg_namelen=29, msg_iov=[{iov_base="This is a test!!\n", iov_len=17}], msg_iovlen=1, msg_control=[{cmsg_len=28, cmsg_level=SOL_SOCKET, cmsg_type=SCM_CREDENTIALS, cmsg_data={pid=32408, uid=0, gid=0}}], msg_controllen=28, msg_flags=0}, MSG_NOSIGNAL) = -1 ESRCH (No such process)
sendmsg(5, {msg_name={sa_family=AF_UNIX, sun_path="/run/systemd/journal/syslog"}, msg_namelen=29, msg_iov=[{iov_base="This is a test!!\n", iov_len=17}], msg_iovlen=1, msg_control=[{cmsg_len=28, cmsg_level=SOL_SOCKET, cmsg_type=SCM_CREDENTIALS, cmsg_data={pid=518, uid=0, gid=0}}], msg_controllen=28, msg_flags=0}, MSG_NOSIGNAL) = -1 ENOENT (No such file or directory)
```

可以看到system-journal确实打开了/dev/log套接字
```
[ssh_10.90.2.251] root@localhost: dev$fuser -v /dev/log
                     USER        PID ACCESS COMMAND
/dev/log:            root          1 F.... systemd
                     root        518 F.... systemd-journal
[ssh_10.90.2.251] root@localhost: dev$lsof -p 518
COMMAND   PID USER   FD      TYPE             DEVICE SIZE/OFF     NODE NAME
systemd-j 518 root  cwd       DIR              253,0      236       64 /
systemd-j 518 root  rtd       DIR              253,0      236       64 /
systemd-j 518 root  txt       REG              253,0   346152 33986071 /usr/lib/systemd/systemd-journald
systemd-j 518 root    0r      CHR                1,3      0t0     1028 /dev/null
systemd-j 518 root    1w      CHR                1,3      0t0     1028 /dev/null
systemd-j 518 root    2w      CHR                1,3      0t0     1028 /dev/null
systemd-j 518 root    3u     unix 0xffffa128efcf0cc0      0t0    10501 /run/systemd/journal/stdout
systemd-j 518 root    4u     unix 0xffffa128efcf1100      0t0    10504 /run/systemd/journal/socket
systemd-j 518 root    5u     unix 0xffffa128efcf1540      0t0    10506 /dev/log
systemd-j 518 root    6w      CHR               1,11      0t0     1034 /dev/kmsg
systemd-j 518 root    7u  a_inode               0,10        0     6595 [eventpoll]
systemd-j 518 root    8u      CHR               1,11      0t0     1034 /dev/kmsg
systemd-j 518 root    9r      REG                0,3        0    10601 /proc/sys/kernel/hostname
systemd-j 518 root   10u  a_inode               0,10        0     6595 [signalfd]
systemd-j 518 root   11u     unix 0xffffa128efcf7b40      0t0    13698 socket
systemd-j 518 root   12u  a_inode               0,10        0     6595 [timerfd]
systemd-j 518 root   13u      REG               0,19  8388608   658324 /run/log/journal/ee11f9993f9d35349ee53d275c088fdc/system.journal
systemd-j 518 root   14u     unix 0xffffa128f33f6e80      0t0    13800 /run/systemd/journal/stdout

```

发现有一个残留的systemd-journald进程?
```
[ssh_10.60.5.113] root@node7: ~$ps -ef | grep journal
root      8906     1  0 20:02 ?        00:00:00 /usr/lib/systemd/systemd-journald
root     23150     1  0 Oct24 ?        00:14:08 /usr/bin/dockerd-current --add-runtime docker-runc=/usr/libexec/docker/docker-runc-current --default-runtime=docker-runc --authorization-plugin=rhel-push-plugin --exec-opt native.cgroupdriver=systemd --userland-proxy-path=/usr/libexec/docker/docker-proxy-current --init-path=/usr/libexec/docker/docker-init-current --seccomp-profile=/etc/docker/seccomp.json --selinux-enabled --log-driver=journald --signature-verification=false --storage-driver overlay2 --add-registry docker.io --add-registry registry.fedoraproject.org --add-registry quay.io --add-registry registry.access.redhat.com
root     23444 23320  0 Oct24 ?        00:04:36 /usr/lib/systemd/systemd-journald
root     26997 46074  0 20:09 pts/7    00:00:00 grep --color=auto journal
```

Warning: Journal has been rotated since unit was started. Log output is incomplete or unavailable.
=> 仅仅因为日志被清掉的原因，没有关系

新版本 coreos 日志已经不是/dev/log了
```
[core@master1 ~]$ echo 'This is a test!!' | nc -u -U /run/systemd/journal/dev-log
```

## 参考资料

* [CentOS7的journalctl日志查看方法](https://www.cnblogs.com/ggzhangxiaochao/p/13953887.html)
* [journalctl 清理journal日志](https://www.cnblogs.com/jiuchongxiao/p/9222953.html)

10分钟教你如何划重点——Sys temd最全攻略
https://developer.aliyun.com/article/810592

systemd基本使用
https://www.cnblogs.com/mikeguan/p/7503341.html

配合 syslog 使用
systemd 提供了 socket /run/systemd/journal/syslog，以兼容传统日志服务。所有系统信息都会被传入。要使传统日志服务工作，需要让服务链接该 socket，而非 /dev/log（官方说明）。Arch 软件仓库中的 syslog-ng 已经包含了需要的配置。

https://documentation.suse.com/zh-tw/sles/12-SP5/html/SLES-all/cha-journalctl.html
systemd 取代 SUSE Linux Enterprise 12 中的傳統 init 程序檔後 (請參閱第 13 章 「systemd 精靈」)，引入了自身的記錄系統日誌。由於所有系統事件都將寫入到日誌中，因此，使用者不再需要執行基於 syslog 的服務。

https://www.jianshu.com/p/2b30bf6f9276
Journal是systemd 为自己提供的日志系统。使用systemd日志，无须额外提供日志服务（syslog）。读取日志的命令：

Journal log 兼容syslog, 即通过syslog(3) 打印的log 也会存储到 Journal log 中.
systemd-journald 通过监听 socket /run/systemd/journal/dev-log 获取到 syslog(3). 因为通常在装有systemd的系统中 /dev/log 是 /run/systemd/journal/dev-log 的一个软连接，而syslog(3)会将log 发送到/dev/log

systemd 提供了 socket /run/systemd/journal/syslog，以兼容传统日志服务。所有系统信息都会被传入。要使传统日志服务工作，需要让服务链接该 socket，而非 /dev/log（官方说明）。
