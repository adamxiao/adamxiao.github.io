## kdump定制

## kylin coreos配置kdump

开启kdump服务:
安装rpm-ostree override replace kexec-tools-2.0.20-16.kb3.ky3.aarch64.rpm 后，重启系统
mount -o remount,rw /boot
mount -o remount,rw /usr
按kdump1.png中所示修改kdumpctl，重启kdump服务

简单配置1024M内存, 内核就预留了内存, 但是kdump服务由于kexec版本问题, 起不来, 替换kexec版本之后可以了!
```
crashkernel=1024M
```

https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/8/html/managing_monitoring_and_updating_the_kernel/configuring-kdump-on-the-command-line_managing-monitoring-and-updating-the-kernel

发现没有内存
```
makedumpfile --mem-usage /proc/kcore
```

修改内核参数: => 提示没有预留内存
```
crashkernel=8196M
```

这个可以makedumpfile
```
crashkernel=256M,low crashkernel=512M,high
```

关键是kexec -s -d -p xxx
realloc(): invlalid pointer
core dump

关键字《kexec realloc invalid pointer》
https://gitee.com/openeuler/community/issues/I1AK8F
=> 感觉跟这个问题很像, kexec-tools导致，需要增加高端内存申请功能的支持，已在你们开源的kexec-tools中找到相关的patch。

## 旧的资料

云桌面定制系统包括 Baremetal、TC、VDE-I和VDE-P等系统，目前发现部分系统的kdump不生效，例如瘦VDE系统。

检查方式：

1. 查看kdump服务是否启动

cat /proc/cmdline | grep crashkernel
systemctl status kdump.service

2. 手动触发crash

echo 1 > /proc/sys/kernel/sysrq
echo c > /proc/sysrq-trigger

3. 观察机器是否自动重启，并检查/var/crash/目录下是否有产生vmcore 文件和vmcore-dmesg.txt日志

ls /var/crash/
127.0.0.1-2019-11-13-03:04:07  127.0.0.1-2019-11-13-03:21:05
ls /var/crash/127.0.0.1-2019-11-13-03:04:07
vmcore  vmcore-dmesg.txt


# vim /boot/grub2/grub.cfg
追加参数"crashkernel=auto"
# grubby --update-kernel=/boot/vmlinuz-3.10.0-693.ky3.kb7.ksvd2.x86_64 --args="crashkernel=auto"
# grubby --info=ALL
# systemctl enable kdump.service
# uname -r
3.10.0-693.ky3.kb7.ksvd2.x86_64
安装和内核版本一致的 kernel-debuginfo 包
# yum install http://192.168.120.17/kojifiles/packages/kernel/3.10.0/693.ky3.kb7.ksvd2/x86_64/kernel-debuginfo-common-x86_64-3.10.0-693.ky3.kb7.ksvd2.x86_64.rpm
# yum install http://192.168.120.17/kojifiles/packages/kernel/3.10.0/693.ky3.kb7.ksvd2/x86_64/kernel-debuginfo-3.10.0-693.ky3.kb7.ksvd2.x86_64.rpm
# yum install http://192.168.120.17/kojifiles/packages/crash/7.1.9/2.ky3.kb5/x86_64/crash-7.1.9-2.ky3.kb5.x86_64.rpm
# reboot
# cat /proc/cmdline
BOOT_IMAGE=/boot/vmlinuz-3.10.0-693.ky3.kb7.ksvd2.x86_64 root=UUID=391d1952-c886-4390-8ed0-9247ade0b91f ro rhgb quiet LANG=zh_CN.UTF-8 intel_iommu=on ksvdgpu rdblacklist=nouveau rdblacklist=snd-hda-intel vga=895 crashkernel=auto
# echo 1 > /proc/sys/kernel/sysrq
# echo c > /proc/sysrq-trigger
参考资料：
https://www.ibm.com/developerworks/cn/linux/l-cn-kdump1/index.html

不错的文章
https://linux.cn/article-8737-1.html
验证kdump效果
1. vmware kylin3.3-4 memory 1G, kdump服务没有起来，提示内存不够
内存加到2G之后，正常启动了。
测试出vmcore 48M， vmcore-dmesg 125K

2. vmware kylin 3.3-4 server版本，内存1G，kdump服务也没有起来，提示内存不够

3. 腾讯云的ubuntu镜像，kdump服务默认没有起来
腾讯云的/proc/cmdline
BOOT_IMAGE=/boot/vmlinuz-4.15.0-54-generic root=UUID=5ba34c3d-bd14-451d-a7d8-09a64009e3f1 ro net.ifnames=0 biosdevname=0 console=ttyS0,115200 console=tty0 panic=5 crashkernel=1800M-64G:160M,64G-:512M

4. 61的云桌面，kylin 3.3-4没有cmdline crashlog
5. 61的云桌面，kylin 3.3-6正常启动了kdump服务
6. vmware 胖vde，内存1G不够，2G正常，且内核选项之后两个，一个是recover
7. vmware瘦vde，内存1G不够，2G不够，4G,8G也启动kdump服务失败
后来在8G状态下把crashkernel=256M，暂没有提示没内存了，
但是报了一个错误，Failed to install module kvmgt


