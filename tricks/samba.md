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
