# truenas安装使用

我之前默认使用uefi安装的, bios安装也行

很容易安装，主要是设置web用户admin密码, 以及配置网络
配置网络先在linux后台配置(控制台有问题?), 然后再web页面上固定网络配置。

#### 配置静态ip地址

在控制台配置:

- 1.首先选择`1) Configure network interface`
  配置网卡为静态模式，以及静态ip地址
  - 配置ipv4_dhcp: no
  - 配置alias: 10.90.3.25/24
  - 最后要测试一下，然后生效持久化保存
- 2.然后选择`2) Configure network settings`
  配置默认网关
  - 配置ipv4gateway: 10.90.3.1

#### iscsi创建

关键字《truenas set iscsi》

参考: https://www.informaticar.net/how-to-create-iscsi-target-in-truenas/

From the left menu select Sharing | Block Shares (iSCSI) | click on Wizard in top right part of the screen.

监听地址一定要选择一个

ipsan iscsi相关概念:
- target
- init
- lun

[4创建iSCSI共享存储](https://juejin.cn/post/7136917385142861854)

- Portals
  TrueNAS对外提供服务时，监听的IP地址
- Initiators Groups
  配置允许发现和挂载TrueNAS的客户端
- Targets
  组合Portals、Initiators Groups的配置
- Extents
  Zvol和extends绑定，才能被服务器或其它设备识别，挂载成硬盘
- Assciated Targets
  将target和extends关联，这是最终被用来发现的共享存储

Portals --- (Targets) --- Initiators Groups
=> 最终客户端就会发现这些targets...
Targets --- (Assciated Targets) --- Extents
=> 最终决定target上有几块硬盘可以用
Portals --- Authorized Access
=> 可以配置CHAP认证接入

[网络存储（四）之ISCSI的进阶](https://www.cnblogs.com/liaojiafa/p/6047550.html)

任何知道target name的客户端都可以随意连接ISCSI服务器, 需要授权区分
例如: 只允许客户端主机A连接target共享出来的磁盘分区1，而客户端主机b只运行连接target分享的磁盘分区2，在这种情况下，就需要在ISCSI target主机上进行授权设定了。

- 通过ip来限定客户端连接不同的磁盘或者分区
- 通过用户名密码连接不同的磁盘或分区

#### iscsi不同客户端发现不同的target

只有配置Initiators Groups才行

然后不同的target配置不同的CHAP认证模式

## 系统配置备份

https://zhuanlan.zhihu.com/p/481986009

参考官方功能文档： System Config Backups | (truenas.com)
支持手动和自动两种方式：
手动备份在 System > General 菜单点击SAVECONFIG

#### 使用rsync给服务器备份文件

参考: https://www.utopiafar.com/2022/02/22/backup_remote_files_with_truenas/
创建一个rsync任务, 使用密钥, pull服务器的目录

## 配置服务

#### 配置http服务

使用容器应用，部署nginx容器

#### 配置dnsmasq服务

=> 后来最简单使用dnsmasq命令启动dhcp服务的... 需要创建配置文件/etc/dnsmasq.conf
  => 然后配置`Cron Jobs`和`Init/Shutdown Scripts`来保持dnsmasq进程的运行?

关键字《truenas scale setup dnsmasq》

https://www.truenas.com/community/threads/trying-to-setup-dnsmasq-in-jail.17088/
=> 这个是truenas core(freebsd)的用法

```
pkg install dnsmasq
edit /usr/local/etc/dnsmasq.conf
edit /etc/rc.conf and added
dnsmasq_enable="YES"
```

[TrueNAS SCALE APP应用安装教程，自定义app安装](https://www.truenasscale.com/2021/12/10/67.html)
介绍
TrueNAS SCALE不仅有很多可以直接安装的应用，还支持自定义安装其他的容器镜像。在SCALE里有2种安装自定义应用的方式。
弄懂了自定义应用的安装，其他所有的应用都是一样的

系统自带（官方的）启动docker镜像
Truecharts社区的custom-app
这两个不同点在于：
- 启动docker镜像**可以设置独立的网络接口和IP**，但是不能反向代理，默认不能和其他应用内部通信。
- custom-app可以使用社区的traefik反向代理，集成有健康检查，运行权限控制等
  个人推荐使用custom-app

启动docker镜像, 设置网络:
- 主机接口：选择你的主网络接口
- IPAM Type：选择静态ip，这里不能选择dhcp，因为每次重启容器的MAC地址都会改变，所以你如果选择dhcp的话，它的IP会一直的改变，所以只能选择静态IP。

#### 加密

关键字《truenas scale lock dataset》

https://www.truenas.com/community/threads/lock-an-encrypted-dataset.90364/
From my experience, once unlocked, the only way to re-lock an encrypted dataset that uses a keyfile is to disconnect the pool. Until then, the keyfile lives on the boot pool. For passphrase protected datasets, you can lock them at will.

只有使用密码加密的datasets，才可以主动加密，解密

[Storage Encryption](https://www.truenas.com/docs/scale/scaletutorials/storage/datasets/encryptionscale/)

You can only lock and unlock an encrypted dataset if it is secured with a passphrase instead of a key file. Before locking a dataset, verify that it is not currently in use.

## 常用配置

常用安全配置:

- 配置强制跳转https
  System Settings -> General -> GUI Settings -> HTTPS Redirect
- 禁用免密控制台
  System Settings -> Advance -> Console -> Show Text Console without Password Prompt

## FAQ

- 虚拟机使用磁盘创建pool, 需要uuid
- NFS共享默认是v3协议,需要手动开启v4协议
- samba默认不开启v1认证支持,windows10不能挂载
- ftp需要用户有主目录?

- 修改iscsi chap密码，居然不是实时生效?
  重启生效, 看有什么方法不重启生效?

#### 怎么同步手动打的名称为xxx的快照到另一个truenas

#### Read-only file system 30

https://www.truenas.com/community/threads/encountered-read-only-file-system-problem-unable-to-create-anything.53756/
```
zfs get readonly
zfs set readonly=off data1/adam-backup
```

## 其他

https://best.pconline.com.cn/yuanchuang/10367901.html
「NAS」小白必读，从入门到上手，保姆级干货分享。 

个人家庭需要nas做什么:
- 家庭影音数据中心
  视频，照片
- 文件备份同步共享
- 资源下载
- 其他高阶应用
  内建数据库，Web服务，搭建个人网站服务器，代码仓库管理，OA/CRM/多人协同办公等等，这些更适合于企业使用，对于大多数普通人来用不到

关键字《pc作为nas》

https://www.v2ex.com/t/860922
- 1. 能耗
- 2. 体积
- 3. 噪音（风扇导致的，硬盘不计）

https://zhuanlan.zhihu.com/p/138153055
购买nas硬件, 搭建windows简单nas

https://www.zhihu.com/question/499638319
近期，看到关于【NAS】的描述，觉得很适合，但仔细看了一下，又很茫然。
- 1.有现成的【NAS】出售
- 2.有购买配件组装【NAS】
- 3.个人电脑配件改造【NAS】
- 4.个人电脑直接换个系统=【NAS】

快照使用(samba挂载网络文件)
管理快照任务
- 每小时快照: 保留一周
- 每周周日快照: 保留一月
- 每1月1日快照: 保留一年

配置rsync服务, 定时拉取待备份的数据!

[高性能家用 NAS 搭建（TrueNAS SCALE）](https://www.zhihu.com/tardis/zm/art/440149283?source_id=1003)

#### 手机照片同步

手机安装一个app即可, 例如pho sync, 支持SMB, NFS, WDAV等协议

#### 电视看电影

关键字《nas电影app》

[我的NAS 篇六：番外篇——用各种设备看NAS里面的电影](https://post.smzdm.com/p/az59vgp0/)
https://post.smzdm.com/p/aen2z7g4/

安装kodi应用，挂载nfs目录使用?

[家庭影音搭建大碗篇丨软件推荐、NAS、流媒体教程一篇打尽](https://www.zhihu.com/tardis/zm/art/408177850?source_id=1003)

https://www.stephenwxf.com/post/90.html
Plex是一整套完整的解决方案，采用Server + Client的形式，Server端用于管理各种媒体（电影，电视剧，照片，音乐、有声小说），Client端用于播放（有Mac，PC，iOS，Android，XBox，PS，各种TV，树莓派等）。需要注意的是PLEX的客户端需要付费才能解决多设备限制。

## 参考资料

https://blog.51cto.com/riverxyz/4572290

- [youtube视频 - 好消息：文件全删！坏消息：还能找回来～](https://www.youtube.com/watch?v=_b83F55c_Yc)

- [Truenas Scale基础入门设置](https://blog.csdn.net/qq_34419607/article/details/123516761)

- [TrueNAS SCALE APP应用安装教程，自定义app安装](https://www.truenasscale.com/2021/12/10/67.html)
