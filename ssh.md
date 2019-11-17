# ssh

## ssh直接信任服务器

```
StrictHostKeyChecking no
UserKnownHostsFile /dev/null
```

## ssh连接很慢的问题

原因一:
ssh对ip进行dns反查超时导致

修改/etc/ssh/sshd_config

```
UseDNS no
UsePAM no
```

或者修改服务器的/etc/hosts文件
加一个ssh client的ip的伪域名
```
1.2.3.4 test.iefcu.cn
```

参考:
https://unix.stackexchange.com/questions/298698/ssh-very-slow-connection

查问题原理(非常好)
https://blog.tanelpoder.com/posts/troubleshooting-linux-ssh-logon-delay-always-takes-10-seconds/
