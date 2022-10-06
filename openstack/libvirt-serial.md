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
