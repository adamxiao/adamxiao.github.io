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

## 参考资料

https://blog.51cto.com/riverxyz/4572290
