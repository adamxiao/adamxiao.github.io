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

#### ls: Fatal error: Certificate verification: Not trusted

ftp服务器证书有问题

https://serverfault.com/questions/411970/how-to-avoid-lftp-certificate-verification-error
```
lftp ftp://$(FTP_USER)@$(FTP_HOST) -e "set ftp:ssl-allow no; mirror -R $(OUTPUTDIR) $(FTP_TARGET_DIR) ; quit"
```
=> 验证发现`ftp:ssl-allow no`参数生效可以用

~/.lftprc
```
set ssl:verify-certificate false
```
=> 验证发现虽然没有告警，但是还是连接失败

https://askubuntu.com/questions/323284/ftps-client-preferably-integrated-in-nautilus
=> nautilus使用ftps://x.x.x.x也不行

[FTP client list and installation on Ubuntu 20.04 Linux Desktop/Server](https://linuxconfig.org/ftp-client-list-and-installation-on-ubuntu-20-04-linux-desktop-server)
=> ubuntu安装其他软件使用吧，配置使用明文? 或者信任证书
```
sudo apt install filezilla
sudo apt install gftp
```
=> 例如filezilla，File -> Site Mananger -> Encryption -> Only use plain FTP(insecure)

#### 连接ftp服务器私有ip失败

strace发现居然连接了私有ip地址
```
2450  read(4, "227 Entering Passive Mode (192,168,11,2,83,245).\r\n", 65536) = 50
2450  read(4, 0x56414f074f00, 65536)    = -1 EAGAIN (Resource temporarily unavailable)
2450  getpeername(4, {sa_family=AF_INET, sin_port=htons(21), sin_addr=inet_addr("10.90.4.4")}, [28->16]) = 0
2450  connect(5, {sa_family=AF_INET, sin_port=htons(21493), sin_addr=inet_addr("192.168.11.2")}, 16) = -1 EINPROGRESS (Operation now in progress)
```

关键字《ftp协议 弹性ip》

https://www.huoban.com/news/post/5673.html

三、解决方案

1、  客户端IE修改为主动模式

如下图所示所示，在“工具->Internet选项->高级”将“使用被动FTP…“勾选去掉。前面说过，FTP主动模式下，FTP服务器会

但有一点需要注意，如果客户端本地网络是通过NAT方式访问外网的，也可能会有问题，所以不建议采用该方案。

2、服务端配置“FTP防火墙支持”

如下图所示，在“防火墙的外部IP地址”中填写主机的弹性公网IP即可，此时仍然采用FTP被动模式。建议使用该种方式，该种方法可以支持被动模式访问FTP，且对客户端本地网络无特殊要求。

注意：被动模式下，FTP服务器的安全组入方向需要放通FTP数据通道的端口号（默认为1024~65535的端口号），否则，FTP服务器也无法访问。如上图所示，此处FTP服务器数据通道端口设置为1025~10018，所以FTP服务器网卡对应安
全组主要添加如下入方向规则，如下图所示。

以上，是在华为云上如何使用华为云弹性云服务器ECS搭建FTP的实践。

https://www.helloworld.net/p/9777430395
后者配置ftp服务器配置把ip地址改成公网ip地址(或者域名)
```
echo "pasv_address=<FTP服务器公网IP地址>" >> /etc/vsftpd/vsftpd.conf #本教程中为ECS服务器弹性IP
```

其他ftp工作原理
https://zhuanlan.zhihu.com/p/34109504
https://www.cnblogs.com/luoxn28/p/5585458.html


#### lftp配置主动模式

https://blog.csdn.net/dliyuedong/article/details/18013267

ftp传输有2种模式，一种主动模式，一种被动模式。主动模式下服务器使用20端口进行数据的传输，被动模式下，服务器使用大于1024的端口进行传输，看似2种模式区别不大，仅仅是一个端口的区别，但是对于安全级别比较高的red hat以及centos等，端口的数据传输都需要经过防火墙的允许，而ubuntu下默认防火墙规则为空。我的lftp之前将配置文件中的模式改为了主动模式，即

```
set ftp:passive-mode off
```

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
