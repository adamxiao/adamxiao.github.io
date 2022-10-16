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

## 参考资料

* [CentOS7的journalctl日志查看方法](https://www.cnblogs.com/ggzhangxiaochao/p/13953887.html)
