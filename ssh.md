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

## ssh正确密码无法登录

原因是ssh root连续登录错误几次，就锁定了!
xzj使用scp输错密码导致

关键字《ssh root密码遭受到攻击，无法密码登录》

/var/log/secure
```
sshd[10619]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=10.30.2.50  user=root
sshd[10619]: Failed password for root from 10.30.2.50 port 54104 ssh2
sshd[10619]: pam_faillock(sshd:auth): Consecutive login failures for user root account temporarily locked
```

ssh密码错误次数过多密码被拒绝
https://juejin.cn/s/ssh%E5%AF%86%E7%A0%81%E9%94%99%E8%AF%AF%E6%AC%A1%E6%95%B0%E8%BF%87%E5%A4%9A%20%E5%AF%86%E7%A0%81%E8%A2%AB%E6%8B%92%E7%BB%9D

https://superuser.com/questions/1597162/how-to-unlock-linux-user-after-too-many-failed-login-attempts
锁定后，可以手动解锁
```
# faillock --user myUsername
# faillock --user myUsername --reset
# rm /var/run/faillock/myUsername
```

## 客户端禁用GSSAPI

https://blog.csdn.net/lufeisan/article/details/53002556
用ssh -v user@server 可以看到登录时有如下信息：
```
debug1: Next authentication method: gssapi-with-mic
debug1: Unspecified GSS failure. Minor code may provide more information
```
可以禁用这个配置
```
ssh -o GSSAPIAuthentication=no user@server
```
使用strace查看后发现，ssh在验证完key之后，进行authentication gssapi-with-mic，此时先去连接DNS服务器，在这之后会进行其他操作

## ssh登录之后bash很慢

strace发现是gluster的complete命令很慢
