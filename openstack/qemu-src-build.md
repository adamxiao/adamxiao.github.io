# 源码编译qemu

## ubuntu编译

```
git clone https://git.qemu.org/git/qemu.git
warning: redirecting to https://gitlab.com/qemu-project/qemu.git/

cd qemu
git submodule init
git submodule update --recursive
Copy
编译安装
./configure
make
```

依赖包获取
```
# ERROR: glib-2.48 gthread-2.0 is required to compile QEMU
sudo apt install -y libglib2.0-dev

# ERROR: pixman >= 0.21.8 not present.
#        Please install the pixman devel package.
sudo apt install -y libpixman-1-dev
```

## openeuler qemu

```
git clone -b openEuler-21.03 https://gitee.com/openeuler/qemu.git
./configure
make

./configure --enable-kvm --target-list=x86_64-softmmu --enable-debug --enable-trace-backends=log --enable-profiler --enable-linux-aio
make -j8 -Wno-error
```

## 运行qemu

```
qemu-system-x86_64 -m 512 -smp 4 --enable-kvm –boot order=dc -hda /root/howl/vm1.qcow2 -cdrom /root/howl/SLES_SP1_x 86_64.iso

./qemu-system-x86_64 -m 1000 -smp 2,sockets=1,cores=2,threads=1 \
  -drive file=/home/xy/centos-ksvd2020.qcow2,if=none,id=drive-virtio0,cache=none -device virtio-blk-pci,drive=drive-virtio0,id=virtio0,bus=pci.0,addr=0xa,bootindex=100,serial=8023543499286-0
gtk initialization failed

 -nographic 

或者用-display vnc=0.0.0.0:1
-vnc 0.0.0.0:11
```

果然，需要启用accel=kvm, 才会进入到handle_io函数中(accel/kvm/kvm-all.c)
```
-machine pc-i440fx-rhel7.6.0,accel=kvm,usb=off,dump-guest-core=off
-machine pc-i440fx-4.1,accel=kvm,usb=off,dump-guest-core=off \
```

qemu-system-x86_64: failed to initialize KVM: Permission denied

## 参考资料

[Compile qemu on Ubuntu 20.04](https://bevisy.github.io/p/compile-qemu-on-ubuntu-20.04/)
