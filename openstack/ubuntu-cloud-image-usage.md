# ubuntu cloud镜像使用

## ubuntu cloud镜像

问题:
- 不能自动扩容文件系统?
- 没有qga，不能在线修改密码
- 没有生成netplan默认dhcp网络配置

### 下载镜像

参考openstack中的获取ubuntu镜像
https://docs.openstack.org/image-guide/obtain-images.html

关键字《ubuntu-20.04-server-cloudimg-amd64-disk-kvm.img 不能用》

镜像列表
- ubuntu-20.04-server-cloudimg-amd64-disk-kvm.img
  名字中带有disk-kvm是什么作用?
  grub启动失败: `GRUB_FORCE_PARTUUID set, attempting initrdless boot.`
- ubuntu-20.04-server-cloudimg-amd64.img
  => 可以用
- focal-server-cloudimg-arm64.img
  有cloudinit?
  => pty控制台能使用，vnc没有shell?

### 用户密码配置

focal-server-cloudimg-xxx 这些镜像是为云环境创建的, 会配合一个init脚本(或者iso)启动并创建普通用户, 默认root不能登录也没有密码, 而单机运行还是需要root的, 所以在安装前, 要设置一下root口令:
```
virt-customize -a some.qcow2c --root-password password:[your password]
```

### 镜像扩容

ubuntu的cloud镜像没有自动扩容的功能, 需要自己手动扩容?

## debian cloud镜像使用

优点:
- 文件系统会自动扩容
- 镜像模板非常小

问题:
- 没有安装qga, 无法在线修改密码功能?
- debian的网络配置，我不熟悉, 不是nmcli, 也不是netowrk, 也不是netplan
- 关键是还没有开启ssh服务? (debian 11?)
  => 原来是no hostkeys available => ssh-keygen -A
  还一定要密钥登录。。。

debian 10镜像都可以的样子?

- debian-10-generic-amd64.qcow2
- debian-10-openstack-amd64.qcow2
- debian-10-openstack-arm64.qcow2

debian 11
- debian-11-generic-amd64-20230501-1367.qcow2
  => 可以用
- debian-11-generic-arm64-20230124-1270.qcow2
  => 不行, 一直黑屏?

#### 镜像格式

debian 11 x86
```
Disk /dev/nbd0: 2147 MB, 2147483648 bytes, 4194304 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: gpt
Disk identifier: 0AC3B12E-66F0-2D42-83EF-E6E4C0179E1A


#         Start          End    Size  Type            Name
 1       262144      4194270    1.9G  Linux filesyste
14         2048         8191      3M  BIOS boot
15         8192       262143    124M  EFI System
```

debian 11 arm
```
Disk /dev/nbd0: 2147 MB, 2147483648 bytes, 4194304 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk label type: gpt
Disk identifier: 3B1412AE-1A6E-4143-973E-981CDF9F832C


#         Start          End    Size  Type            Name
 1       262144      4194270    1.9G  Linux filesyste
15         2048       262143    127M  EFI System
```

## centos cloud镜像使用

- centos7 x86镜像
  用的最多的，不错!
- centos7 arm
  每次都卡在cloudinit中..., 不是很好用

## windows cloud镜像使用

- win2022en-standard-minimal.vmdk
  大小11G, 网上下载到的, 不支持uefi启动!
  => 首次启动, 需要花费比较长的时间, 可以页面设置密码
  => 感觉应该比较好用!

记得之前下载过一个win2012-server的，忘了在哪里了，使用了sysgrep吧!
