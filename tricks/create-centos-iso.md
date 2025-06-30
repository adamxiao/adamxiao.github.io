# 创建修改CentOS系列ISO镜像

（三）安装制作ISO的工具
```
yum  -y install createrepo mkisofs isomd5sum rsync
```

（四）建立 image-making-directory
（1）创建 ISO制作目录
```
mkdir -p /data/centos-new-dir
```
（2）挂载官方ISO镜像文件
```
mount /dev/xxx.iso /mnt
```

（3）把官方镜像里的文件同步到image-making-directory
```
rsync -avh /mnt/ /data/centos-new-dir/
```

（六）替换Packages/里的文件
```
cp xxx.rpm Packages/
```

更新软件源
```
createrepo -d -g repodata/*-comps.xml .
```

（十）制作ISO
```
mkisofs -o /data/centos-new.iso -input-charset utf-8 -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -R -J -v -T -joliet-long -V EVGLOW /data/centos-new/
# 更新md5sum
implantisomd5 /data/centos-new.iso
```

819的制作方法(参考os组的mkiso.sh) => ok
=> 是efi启动?
```
mkisofs -v -U -J -R -T \
  -m repoview -m boot.iso \
  -eltorito-alt-boot -e images/efiboot.img -no-emul-boot -V KylinSec \
  -o /data/ksvd-new.iso /data/centos-new-dir
implantisomd5 /data/ksvd-new.iso
```

TODO: mkisofs相关参数说明
- -m repoview
  exclude，去除文件
- -o xxx.iso
  生成iso路径

#### iso镜像kickstart定制自动安装

gpt《修改openEuler ISO kickstart文件》
openEuler-22.03-LTS-SP3-x86_64-dvd.iso
修改里面的kickstart文件，然后重新制作为iso镜像

修改 ISO 引导配置
```
# 修改自动安装选项（示例）
sed -i 's/quiet/quiet inst.ks=cdrom:\/ks.cfg/' ~/iso/modified/isolinux/isolinux.cfg
=> 或者是 EFI/BOOT/grub.cfg
```
=> openueler的iso镜像默认没有指定ks文件，需要增加`inst.ks=cdrom:/ks/ks.cfg`

然后生成iso镜像，注意标签为`openEuler-22.03-LTS-SP3-x86_64`

自动安装的kickstart文件参考
```
keyboard --vckeymap=us --xlayouts='us'
lang en_US.UTF-8
rootpw --iscrypted $y$j9T$c7fw7aHlK3QrGWAy0Y/NC.a9$zHFiZgjt9zMAjPHmc17k9M1WjfF1yKeTF0R2QRaHnQ/
# System timezone
timezone Asia/Shanghai --isUtc --nontp
# System bootloader configuration
# Partition clearing information

selinux --disabled
firewall --disabled

# Use hard drive installation media
#harddrive --dir= --partition=LABEL=openEuler-22.03-LTS-SP3-x86_64
network --hostname=node1 --bootproto=static --ip=10.90.6.190 --netmask=255.255.255.0 --gateway=10.90.6.1 --nameserver=192.168.168.168

# Disk partitioning (critical fixes below)
clearpart --all --initlabel --drives=sda
ignoredisk --only-use=sda

# Partition scheme (adjusted sizes)
part /boot --fstype="ext4" --ondisk=sda --size=1024 --asprimary
part /boot/efi --fstype="efi" --ondisk=sda --size=1024 --fsoptions="umask=0077,shortname=winnt"
part pv.111 --fstype="lvmpv" --ondisk=sda --size=409600 --grow --asprimary  # Reduced to 400GB

# LVM configuration
volgroup openeuler --pesize=4096 pv.111
logvol / --fstype="ext4" --size=204800 --grow --name=root --vgname=openeuler  # 200GB
logvol /var/log --fstype="ext4" --size=98304 --name=var_log --vgname=openeuler  # 96GB

%packages --multilib
@^minimal-environment
tar
%end

%post
sed -i '/\/opt\/suzaku\/data/ s/defaults /defaults,sync /' /etc/fstab
%end

# Reboot after installation
reboot
```

或者使用自动分区
```
ignoredisk --only-use=/dev/sda
autopart --type=lvm
clearpart --all --initlabel --drives=/dev/sda
```

## 参考资料

- [定制自己的CentOS，制作ISO镜像文件](https://blog.csdn.net/evglow/article/details/104040243)
