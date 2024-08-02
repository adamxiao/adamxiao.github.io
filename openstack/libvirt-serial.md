# libvirt配置虚拟机串口使用

猜测, 是由于115200没有对应上, 只要配置好就能输出?

## 串口使用

关键字《centos7设备ttyS0波特率》

https://www.cnblogs.com/ggzhangxiaochao/p/13558137.html
```bash
# 查看串口1（/dev/ttyS0）当前的参数，包括波特率、数据位等。
stty -F /dev/ttyS0 -a
```

```bash
#stty设置串口参数
stty -F /dev/ttyS0 ispeed 115200 ospeed 115200 cs8
```


## virsh连接虚拟机串口

通过pty的方式连接
```
virsh console xxx
```

## 调研

h3c可以配置虚拟机使用物理机的串口!

https://10.20.2.219:8443/cas/html/help/plat/zh/default_auto.htm#Quick/ConfigVM.html
我查了一下h3c的文档，确实也提到了串口的使用

增加“串口”：
类型：串口的类型，包括Physical host character device (dev)、Pseudo TTy(pty)，默认为Physical host character device (dev)。
串口号：根据串口号来识别不同的串口。
路径：主机串口路径。如果选择增加dev类型的串口，必须输入可用的路径（如：/dev/ttyS0），否则会导致虚拟机无法启动。


#### 小型设备的串口调试

配置内核参数添加了"console=ttyS0,115200n8", 才可以输出, 否则没有任何相应
```
grubby --update-kernel=/boot/vmlinuz-4.19.90-2003.4.0.0036.ky3.kb29.x86_64 --args="console=ttyS0,115200n8"

# 删除参数
grubby --update-kernel=/boot/vmlinuz-4.19.90-2003.4.0.0036.ky3.kb29.x86_64 --remove-args="console"
```

#### linux查看串口信息

如何查看linux下串口信息
https://blog.csdn.net/JustDoIt_201603/article/details/112032562

```
1、查看串口是否可用，可以对串口发送数据比如对com1口，echo lyjie126 > /dev/ttyS0
2、查看串口名称使用 ls -l /dev/ttyS* 一般情况下串口的名称全部在dev下面，如果你没有外插串口卡的话默认是dev下的ttyS* ,一般ttyS0对应com1，ttyS1对应com2，当然也不一定是必然的；
3、查看串口驱动：cat /proc/tty/driver/serial（可以查看ttyS文件关联的物理串口信息，这个很重要！）
4、查看串口设备：dmesg | grep ttyS
```

例如, 查看串口是否可用, ttyS0可用, ttyS1不可用
```
[root@centos2 ~]# echo fuck > /dev/ttyS1
-bash: echo: write error: Input/output error
[root@centos2 ~]# echo fuck > /dev/ttyS0
[root@centos2 ~]#
```

查看串口驱动
```
$ cat /proc/tty/driver/serial
serinfo:1.0 driver revision:
0: uart:16550A port:000003F8 irq:4 tx:62 rx:26781 CTS|DSR|CD
1: uart:unknown port:000002F8 irq:3
2: uart:unknown port:000003E8 irq:4
3: uart:unknown port:000002E8 irq:3
```

guest查看串口信息
```
# dmesg | grep ttyS
[    0.662070] Serial: 8250/16550 driver, 4 ports, IRQ sharing enabled
[    0.683503] 00:04: ttyS0 at I/O 0x3f8 (irq = 4) is a 16550A
```

https://blog.csdn.net/qq_35358125/article/details/107073694
看一下板子上的串口有没有设备?
```
grep tty /proc/devices
如果有ttyS设备，再看/dev/有没有ttyS*，如没有就建立一个：mknod /dev/ttyS0 c 4 64
如果板子的设备中没有标准串口设备ttyS0，也没有ttySAC0。/dev下应该有一个USB串口：/dev/ttyUSB0.
```

## 其他资料

关键字《libvirt serial type=dev》

[redhat的libvirt串口配置文档](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/virtualization_administration_guide/sub-section-libvirt-dom-xml-devices-host-interface)

Host physical machine device proxy
The character device is passed through to the underlying physical character device. The device types must match, eg the emulated serial port should only be connected to a host physical machine serial port - do not connect a serial port to a parallel port.	
```xml
<devices>
   <serial type="dev">
	  <source path="/dev/ttyS0"/>
	  <target port="1"/>
   </serial>
</devices>
```

[libvirt官方文档 - Host device proxy](https://libvirt.org/formatdomain.html#host-device-proxy)

libvirt官方文档就说明串口设备, 可以为
https://libvirt.org/formatdomain.html#serial-port
* pty
* unix socket
* file
* spice channel等设备

#### 文件串口

关键字《libvirt将虚拟机的串口重定向到文件中》

https://www.rickylss.site/qemu/virsh/2020/05/21/qemu-serial-console/
```
<serial type='file'>
  <source path='/var/log/libvirt/qemu/test.log'/>
  <target type='isa-serial' port='1'>
    <model name='isa-serial'/>
  </target>
</serial>
```

对应qemu参数为
```
-device virtio-serial-pci,id=virtio-serial0,bus=pci.0,addr=0xb

-add-fd set=3,fd=70
-chardev file,id=charserial0,path=/dev/fdset/3,append=on
-device isa-serial,chardev=charserial0,id=serial0
```

5、最终解决方案
实际上有一种方法可以达到既能使用 virsh console 又能输出到本地文件。使用这种方法不需要开启两个 serial，参考 libvirt xml 如下：
```
<log file="/var/log/libvirt/qemu/guest-serial0.log" append="off">
qemu参数里是 -chardev pty,id=charserial0,logfile=/dev/fdset/11,logappend=on
```

#### pty串口

```
<serial type='pty'>
  <target port='1'></target>
</serial>
```

这个使用最简单
```
virsh console ${uuid}
```

#### unix socket串口

```
  <serial type="unix">
    <source mode="bind" path="/tmp/336b.socket"/>
    <target port="1"/>
  </serial>
```

可以通过socat轻松连接使用这个串口
```
socat stdin,raw,echo=0,escape=0x11 "unix-connect:/tmp/336b.socket"

localhost.localdomain
UniKylin 3.3
```

https://forum.proxmox.com/threads/serial-port-between-two-vms.63833/
connect the two serial ports on the host
```
socat UNIX-CLIENT:/tmp/336b.socket UNIX-CLIENT:/tmp/336b-clone.socket
```

## 参考资料

[redhat的libvirt串口配置文档](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/virtualization_administration_guide/sub-section-libvirt-dom-xml-devices-host-interface)

[Accessing libvirt VMs via telnet](https://lukas.zapletalovi.com/2018/02/accessing-libvirt-vms-via-telnet.html)
