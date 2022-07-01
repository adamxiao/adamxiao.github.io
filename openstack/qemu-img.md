# qemu-img 简单使用

转换镜像格式, 转qcow2为vmdk, 给vmware使用
```bash
qemu-img convert -f qcow2 -O vmdk centos7.qcow2 centos7.vmdk
```
