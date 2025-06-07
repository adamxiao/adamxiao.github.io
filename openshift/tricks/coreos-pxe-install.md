# coreos系统pxe安装

## 构建一个pxe dnsmasq服务

pxe-dhcp.conf配置文件内容:
```conf
# cat /etc/dnsmasq.d/pxe-dhcp.conf
interface=enp2s0
bind-interfaces

dhcp-range=10.20.6.220,10.20.6.240,255.255.240.0,1h
dhcp-option=3,10.20.1.1
dhcp-option=6,10.20.1.50

dhcp-match=set:efi-x86_64,option:client-arch,7
dhcp-match=set:efi-x86_64,option:client-arch,9
dhcp-match=set:efi-x86,option:client-arch,6
dhcp-match=set:efi-arm,option:client-arch,11
dhcp-match=set:bios,option:client-arch,0
dhcp-boot=tag:efi-x86_64,shim.efi,,
dhcp-boot=tag:efi-x86,shim.efi,,
dhcp-boot=tag:efi-arm,arm/shim.efi,,
dhcp-boot=tag:bios,pxelinux/pxelinux.0,,

# cat /etc/dnsmasq.d/tftp.conf
enable-tftp
tftp-root=/var/lib/tftp/
```

可以使用dnsmasq容器部署, docker-compose.yml内容如下:
```yaml
version: '3.4'
services:
  dnsmasq:
    image: hub.iefcu.cn/public/dnsmasq:latest
    container_name: pxe-dnsmasq
    restart: always
    network_mode: host
    privileged: true
    volumes:
      - ./dnsmasq.conf:/etc/dnsmasq.conf
      - ./tftpboot:/var/lib/tftp:ro
      - ../pxe:/var/lib/tftp/pxe:ro
    environment:
      - HTTP_USER=adam
      - HTTP_PASS=xxxxxx
    logging:
      driver: json-file
      options:
        max-file: '3'
        max-size: 10m
```

或者独立ip地址
```
docker run -d --name pxe-dnsmasq \
    --network macvlan-net \
    --ip 10.20.1.51 \
    --log-opt "max-size=10m" \
    --restart always \
    hub.iefcu.cn/public/dnsmasq:latest
```

docker创建macvlan网络
```bash
docker network create -d macvlan \
  --subnet=10.20.1.1/20 \
  --gateway=10.20.1.1 -o parent=enp2s0 macvlan-enp2s0
```


## xxx

coreos-install.arm
```bash
# bootstrap =================================================================
cat > grub.cfg-01-f4-8e-38-74-9a-4e << EOF
set timeout=10

menuentry 'Install Red Hat Enterprise Linux CoreOS' --class fedora --class gnu-linux --class gnu --class os {
  linuxefi /pxe/rhcos/vmlinuz ip=10.20.6.100::10.20.1.1:255.255.240.0:bootstrap.ocp4.iefcu.cn:enp2s0:none nameserver=10.20.1.12 ignition.platform.id=metal coreos.live.rootfs_url=http://pxe.ocp4.iefcu.cn/pxe/rhcos/rootfs.img coreos.inst.install_dev=/dev/sda coreos.inst.insecure coreos.inst.ignition_url=http://api.ocp4.iefcu.cn:8080/ignition/bootstrap.ign
  initrdefi /pxe/rhcos/initrd.img
}
EOF


# master1 ==================================================================
cat > grub.cfg-01-70-b5-e8-22-56-43 << EOF
set timeout=10

menuentry 'Install Red Hat Enterprise Linux CoreOS' --class fedora --class gnu-linux --class gnu --class os {
  linuxefi /pxe/rhcos/vmlinuz ip=10.20.6.101::10.20.1.1:255.255.240.0:master1.ocp4.iefcu.cn:enp2s0:none nameserver=10.20.1.12 ignition.platform.id=metal coreos.live.rootfs_url=http://pxe.ocp4.iefcu.cn/pxe/rhcos/rootfs.img coreos.inst.install_dev=/dev/sda coreos.inst.insecure coreos.inst.ignition_url=http://api.ocp4.iefcu.cn:8080/ignition/master.ign
  initrdefi /pxe/rhcos/initrd.img
}
EOF
```


coreos-install.sh.aarch64
```bash
rm -f grub.cfg-*

# bootstrap =================================================================
cat > grub.cfg-01-52-54-84-00-ee-02 << EOF
set timeout=10

menuentry 'Install CoreOS' --class fedora --class gnu-linux --class gnu --class os {
  linux /pxe/rhcos-aarch64/vmlinuz ip=10.90.3.30::10.90.3.1:255.255.255.0:bootstrap.kcp2-arm.iefcu.cn:enp1s0:none nameserver=10.90.3.38 ignition.platform.id=metal coreos.live.rootfs_url=http://10.90.3.38:8080/rhcos-aarch64/rootfs.img coreos.inst.install_dev=/dev/vda coreos.inst.insecure coreos.inst.ignition_url=http://10.90.3.38:9090/bootstrap.ign
  initrd /pxe/rhcos-aarch64/initrd.img
}
EOF


# master1 ==================================================================
cat > grub.cfg-01-52-54-84-00-ee-01 << EOF
set timeout=10

menuentry 'Install CoreOS' --class fedora --class gnu-linux --class gnu --class os {
  linux /pxe/rhcos-aarch64/vmlinuz ip=10.90.3.35::10.90.3.1:255.255.255.0:master1.kcp2-arm.iefcu.cn:enp1s0:none nameserver=10.90.3.38 ignition.platform.id=metal coreos.live.rootfs_url=http://10.90.3.38:8080/rhcos-aarch64/rootfs.img coreos.inst.install_dev=/dev/vda coreos.inst.insecure coreos.inst.ignition_url=http://10.90.3.38:9090/master.ign
  initrd /pxe/rhcos-aarch64/initrd.img
}
EOF
```

#### coreos-pxe.sh.x86.leag

```bash
# bootstrap =================================================================
cat > pxelinux/pxelinux.cfg/01-52-54-84-00-dd-00 << EOF
default menu.c32
timeout 100
menu title kylin

menu title ########## PXE Boot Menu ##########

LABEL rhcos-4.8.2
    KERNEL http://pxe.kylin.cn:8080/pxe/rhcos/vmlinuz
    APPEND initrd=http://pxe.kylin.cn:8080/pxe/rhcos/initrd.img ip=10.90.3.140::10.90.3.1:255.255.255.0:bootstrap.kcp4.kylin.cn:ens3:none nameserver=10.90.3.144 ignition.platform.id=metal coreos.live.rootfs_url=http://pxe.kylin.cn:8080/pxe/rhcos/rootfs.img coreos.inst.install_dev=/dev/vda coreos.inst.insecure coreos.inst.ignition_url=http://pxe.kylin.cn:8080/bootstrap.ign
EOF

# master =================================================================
cat > pxelinux/pxelinux.cfg/01-52-54-84-00-dd-01 << EOF
default menu.c32
timeout 100
menu title kylin

menu title ########## PXE Boot Menu ##########

LABEL rhcos-4.8.2
    KERNEL http://pxe.kylin.cn:8080/pxe/rhcos/vmlinuz
    APPEND initrd=http://pxe.kylin.cn:8080/pxe/rhcos/initrd.img ip=10.90.3.141::10.90.3.1:255.255.255.0:master1.kcp4.kylin.cn:ens3:none nameserver=10.90.3.144 ignition.platform.id=metal coreos.live.rootfs_url=http://pxe.kylin.cn:8080/pxe/rhcos/rootfs.img coreos.inst.install_dev=/dev/vda coreos.inst.insecure coreos.inst.ignition_url=http://pxe.kylin.cn:8080/master.ign
EOF
```

### coreos-ipxe.sh.x86

mac-52548400122f.ipxe
```
#!ipxe

goto deploy

:deploy
imgfree
kernel http://10.30.2.95/rhcos-x86/vmlinuz ip=10.90.4.105::10.90.4.1:255.255.255.0:bootstrap.kcp4.iefcu.cn:enp4s1:none nameserver=10.90.4.107 ignition.platform.id=metal coreos.live.rootfs_url=http://10.30.2.95/rhcos-x86/rootfs.img coreos.inst.install_dev=/dev/vda coreos.inst.insecure coreos.inst.ignition_url=http://10.90.4.107:9090/kcp4.iefcu.cn/bootstrap.ign

initrd http://10.30.2.95/rhcos-x86/initrd.img
boot
```

## 参考文档

* [centos pxe install](https://docs.centos.org/en-US/centos/install-guide/pxe-server/#sect-network-boot-setup-uefi)
