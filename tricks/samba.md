# samba安装使用

linux命令行挂载
```bash
mount -t cifs //10.20.1.50/public /mnt -o rw,username=user,password="xxx"
```

windows命令行挂载
```
net use Z: \\192.168.1.100\public /user:myuser mypassword
net use Z: \\10.90.3.26\public /user:ksvd2 d43cbd5c793ad34967293a0a574e1de1
```

#### 调试日志开启

数字越大，级别越高, 最高是10
```
[global]
    log level = 10 pdb:10
```

手动运行
```
/usr/sbin/smbd --foreground --no-process-group -S
```
