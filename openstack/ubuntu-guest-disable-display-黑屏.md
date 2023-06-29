# ubuntu arm镜像黑屏

思路:

- 参考银河麒麟v10 arm版本上的virt-manager启动虚拟机, 之前使用rhcos可以显示!
  没有video, 有串口
  **居然使用非kvm qemu运行虚拟机...**
- openstack arm版本
- fusion compute arm版本
- https://askubuntu.com/questions/884534/how-to-run-ubuntu-desktop-on-qemu/1046792#1046792
  夏总想让我尝试这个参数... `-vga virtio`, 而libvirt使用的是`-device virtio-gpu-pci`, 是一样的!

ubuntu 16.04 arm版本，在串口pty上使用如下命令输入内容到屏幕上去，居然可以显示!!!
```
echo afdsljflsdajflasdjflasdf > /dev/tty0
为啥tty1不行, 有些系统确实tty1，例如ubuntu 22.04 arm
```

## 其他资料

关键字《ubuntu arm not support virtio video》
[VGA and other display devices in qemu](https://www.kraxel.org/blog/2019/09/display-devices-in-qemu/)

ubuntu 16.04 arm尝试

[QEMU + Ubuntu ARM aarch64](https://gist.github.com/oznu/ac9efae7c24fd1f37f1d933254587aa4?permalink_comment_id=3677029)
=> 发现有个EFI的fd可以下载使用

Get Ubuntu Image and QEMU EFI:
```
wget https://cloud-images.ubuntu.com/releases/16.04/release/ubuntu-16.04-server-cloudimg-arm64-uefi1.img
wget https://releases.linaro.org/components/kernel/uefi-linaro/latest/release/qemu64/QEMU_EFI.fd
```

https://askubuntu.com/questions/1042696/are-there-official-ubuntu-arm-aarch64-desktop-images
```
$ sudo apt update
$ sudo apt install ubuntu-desktop
$ sudo reboot
```

[How to Install a Desktop (GUI) on an Ubuntu Server](https://phoenixnap.com/kb/how-to-install-a-gui-on-ubuntu)


## FAQ

#### ubuntu 16.04 arm版本，使用非lvm安装, 安装后，关机再开机，起不来???

以及安装过程中黑屏, 暂时使用串口安装的...

why?

https://github.com/utmapp/UTM/issues/2333
Ubuntu 20 AArch64 image from gallery can't boot on Apple M1 "BdsDxe: failed to load Boot0001" #2333
=> 看看?

#### error: no suitable video mode found.

```
error: no suitable video mode found.
error: no such device: root.
```
