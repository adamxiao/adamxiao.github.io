# ubuntu下加密使用

[ubuntu下文件加密方法](https://blog.csdn.net/weixin_50511931/article/details/108367964)

准备工作
```
安装
sudo apt-get install ecryptfs-utils
创建登录密码和挂载密码
ecryptfs-setup-private
```

挂载加密文件
```
① 用ecrypt挂载文件夹

	mount -t ecryptfs /mnt/tPrivate /mnt/tPrivate
	
	 ps:在挂载过程中会遇到询问提示

         a 首先需要输入挂载密码（不同于登录密码）

         b 然后需要选择密钥计算方式（直接回车为默认）

         c 接着需要输入加密长度（直接回车为默认）

         d 接着需要选择是否允许将未加密文件放入此文件夹中（默认为不允许）

② 把要加密的文件放到/mnt/tPrivate 文件夹中

③ 卸载文件夹

	umount /mnt/tPrivate 
```

[Ecryptfs企业级加密文件系统](https://wiki.ubuntu.org.cn/Ecryptfs%E4%BC%81%E4%B8%9A%E7%BA%A7%E5%8A%A0%E5%AF%86%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F)

```
sudo mount -t ecryptfs real_path ecryptfs_mounted_path
```

real_path 是真实存放数据的地方；ecryptfs_mounted_path 是指你要把文件夹挂载于哪里（具体位置可以随意）

## 使用lvm加密分区

[The easiest way to install Ubuntu on an encrypted partition](https://maciej-sady.medium.com/the-easiest-way-to-install-ubuntu-on-an-encrypted-partition-a882320dd6bb)
=> 创建一个lvm加密卷作为home分区, 开机时提示解密!

- 使用gparted创建一个lvm2 pv分区

https://www.tecmint.com/encrypt-disk-installing-ubuntu/

lsblk效果
```
└─sdc4             8:36   0   5.7G  0 part
  └─adam-home    253:0    0   5.7G  0 lvm
    └─sda4_crypt 253:1    0   5.7G  0 crypt /home
```

配置fstab
```
/dev/mapper/sda4_crypt                    /home           ext4    errors=remount-ro 0       1
```

### 加密lvm卷

[How To Encrypt Linux Hard Disks Using LUKS](https://oak-tree.tech/blog/lvm-luks)

创建lvm卷
```
pvcreate /dev/sda4
vgcreate adam /dev/sda4
lvcreate -l 100%FREE adam -n home
```

设置加密
```
apt install cryptsetup
cryptsetup luksFormat /dev/adam/home # 设置LUKS
cryptsetup open /dev/adam/home open # 解密卷
mkfs.ext4 -m 1 /dev/mapper/open # 格式化, 注意是格式化open这个解密卷
```

设置开机自动挂载
/etc/crypttab
```
sda4_crypt UUID=7cb1b762-59c9-495d-b6b3-18e5b458ab70 none luks,discard
```

获取加密的uuid
```
cryptsetup luksUUID /dev/adam/home
```

最后配置到/etc/fstab就可以自动挂载了
```
/dev/mapper/open /mnt ext4 errors=remount-ro 0 1
```

