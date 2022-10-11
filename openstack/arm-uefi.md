# libvirt arm uefi支持

## kylinsec 344 arm64使用virt-manager

* 使用光盘源, 安装virt-manager
* 安装edk2-aarch64
* 重启libvirtd即可

#### centos7 arm64支持虚拟化

关键字`centos7 install efi aarch64`

https://blog.csdn.net/c5113620/article/details/115434366

```
yum groupinstall "Virtualization Host" -y
yum install qemu-kvm virt-manager libvirt
```

## 旧的资料

https://ostechnix.com/enable-uefi-support-for-kvm-virtual-machines-in-linux/
virt-manager,以及virt-install
```
virt-install --name centos8 --ram=2048 --vcpus=8 --cpu host --hvm --disk path=/data/vm-images/kylinos-vm1,size=10 --location /data/iso/KylinSec-3.3-9A-2107-101731-aarch64.iso --graphics vnc --boot uefi
```

Did not find any UEFI binary path for arch 'aarch64'

MD,在arm服务器上,ubuntu居然就给我安装了x86的ovmf...

https://www.sysit.cn/blog/post/sysit/%E4%B8%BAKVM%E5%AE%89%E8%A3%85UEFI%E6%94%AF%E6%8C%81
最后发现还是要装edk2包,ubuntu是叫qemu-efi-aarch64



x86 uefi支持



谷歌关键字《virt-manager uefi引导》
KVM虚拟机支持UEFI启动
https://qkxu.github.io/2020/04/17/KVM虚拟机支持UEFI启动.html

使用Qemu在x86_64机器上安装aarch64的ubuntu server 16.04
https://blog.csdn.net/wujianyongw4/article/details/80353892

KVM虚拟机支持UEFI启动
yum install -y edk2.git-ovmf-x64.noarch
yum install -y AAVMF # 测试可以？



修改KVM启动类型为UEFI
https://blog.csdn.net/Y1309SIR/article/details/105385648
现在KVM使用，很多时候都是懒得重新安装系统，然后直接复制img文件，然后进入虚拟机后，对系统做一点修改就可以直接使用了，但是有时候直接替换后，开机连接会无法正常显示界面。

这个是因为我们img文件里面是已经安装好系统了，系统安装的时候可能是使用的BIOS安装，然后你替换后是使用的UEFI安装，由于启动类型的不同，所以到时候开机后画面出错。（如下图所示，本来系统是在BIOS安装的，然后现在用的UEFI启动方式，开机后，画面就不能正常显示了）

[install aarch64 on x86-centos](https://medium.com/%E9%AB%94%E9%A9%97%E4%BA%BA%E7%94%9F-touch-life/install-aarch64-on-x86-centos-c35919f798a9)


## 参考资料
