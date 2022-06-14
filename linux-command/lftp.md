# lftp安装使用

## 安装

ubuntu安装
```bash
apt install lftp
```

macos
```bash
brew install lftp
```

其他可以在ubuntu容器中使用

## 使用

连接ftp服务器
```
lftp 10.0.0.5
```

用户登录
```
> user dev2
输入密码
```

同步目录
```
mirror xxx xxx

# 上传文件夹
mirror -R registry-data .
```

## FAQ

#### 中文乱码问题

https://www.bookstack.cn/read/Open-Source-Travel-Handbook/acba83c0533300a1.md

GB编码仍被广泛使用于Windows系统中，多数ftp服务器使用gb编码传输。而在以UTF-8为locale的Linux系统中，lftp不能自动识别GB编码，故显示为乱码。遇到此问题时，需要通过命令告知lftp以gb编码读取数据。

解决办法, 在lftp命令行中输入：
```
lftp >set ftp:charset gbk   #设置远程编码为gbk
lftp >set file:charset utf8 #设置本地编码(Linux系统默认使用 UTF-8，这一步通常可以省略)
```
即可，第一条命令表示服务器使用GBK编码，第二条表示本地使用UTF-8编码。

如果想设置GBK编码为lftp默认编码（会导致使用UTF-8编码的服务器乱码），可以编辑~/.lftprc或/etc/lftp.conf，在其末尾加入：
```
set ftp:charset gbk
set file:charset utf8
```

## 使用
