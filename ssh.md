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

## Could not open a connection to your authentication agent

ssh-agent程序挂了没起来!

https://stackoverflow.com/questions/17846529/could-not-open-a-connection-to-your-authentication-agent
```
eval `ssh-agent -s`
ssh-add
```

## ssh无法使用秘钥登录

可能有多种原因:
- 服务器秘钥认证文件权限不对(也可能是相关目录权限不对)
- 服务器秘钥认证文件不是.ssh/authorized_keys(服务端可以改变的...)
