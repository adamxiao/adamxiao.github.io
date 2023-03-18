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

## FAQ

- 虚拟机使用磁盘创建pool, 需要uuid
- NFS共享默认是v3协议,需要手动开启v4协议
- samba默认不开启v1认证支持,windows10不能挂载
- ftp需要用户有主目录?

- 修改iscsi chap密码，居然不是实时生效?
  重启生效, 看有什么方法不重启生效?

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

## 参考资料

https://blog.51cto.com/riverxyz/4572290

- [youtube视频 - 好消息：文件全删！坏消息：还能找回来～](https://www.youtube.com/watch?v=_b83F55c_Yc)
