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

## 参考资料

- [定制自己的CentOS，制作ISO镜像文件](https://blog.csdn.net/evglow/article/details/104040243)
