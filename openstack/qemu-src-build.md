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

ubuntu 20.04安装最新版qemu，依赖包处理
```
sudo apt install -y libglib2.0-dev \
  libpixman-1-dev \
  python3.8-dev \
  python3-venv \
  python3-pip \
  ninja-build \
  libaio-dev
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

/usr/libexec/qemu-kvm -vnc 0.0.0.0:11 -m 512 -cpu host -smp 4 --enable-kvm -hda /home/vm-images/centos-ksvd2020.qcow2

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

```
[root@localhost x86_64-softmmu]# ./qemu-system-x86_64 -h | grep trace
-trace [[enable=]<pattern>][,events=<file>][,file=<file>]
```

## qemu io写验证

修改qemu代码，添加日志
(qemu分支stable-4.1)
```
diff --git a/block/block-backend.c b/block/block-backend.c
index 0056b52..3c5a744 100644
--- a/block/block-backend.c
+++ b/block/block-backend.c
@@ -1450,6 +1453,9 @@ BlockAIOCB *blk_aio_pwritev(BlockBackend *blk, int64_t offset,
                             QEMUIOVector *qiov, BdrvRequestFlags flags,
                             BlockCompletionFunc *cb, void *opaque)
 {
+    fprintf(stderr, "blk_aio_pwritev name %s, refcnt %d, offset %ld, bytes %lu, iobuf %p!\n",
+            blk->name, blk->refcnt, offset, qiov->size, qiov);
+
     return blk_aio_prwv(blk, offset, qiov->size, qiov,
                         blk_aio_write_entry, flags, cb, opaque);
 }
```

配置qemu, 进行编译
```
../configure --enable-kvm --target-list=x86_64-softmmu --enable-linux-aio \
--enable-debug --enable-trace-backends=log

../configure --enable-kvm --target-list=x86_64-softmmu --enable-linux-aio \
--enable-debug --enable-trace-backends=log --firmwarepath=/usr/share/qemu-kvm/
```

手动运行qemu测试
```
# strace -o ~/adam.strace.log -f -s 8000 -tt -T
# -nographic
# -vnc 0.0.0.0:1\
./qemu-system-x86_64 -m 1000 -smp 2,sockets=1,cores=2,threads=1 \
  -machine pc-i440fx-4.1,accel=kvm,usb=off,dump-guest-core=off \
  -display vnc=0.0.0.0:1 \
  -drive file=/home/kylin-ksvd/centos-ksvd2020.qcow2,if=none,id=drive-virtio0,cache=none -device virtio-blk-pci,drive=drive-virtio0,id=virtio0,bus=pci.0,addr=0xa,bootindex=100,serial=8023543499286-0
```

## centos7环境处理

缺少依赖
```
ERROR: glib-2.40 gthread-2.0 is required to compile QEMU
ERROR: zlib check failed
       Make sure to have the zlib libs and headers installed.
ERROR: pixman >= 0.21.8 not present.
       Please install the pixman devel package.
ERROR: User requested feature linux AIO
       configure was not able to find it.
       Install libaio devel
```

安装依赖
```
yum install -y glib2-devel zlib-devel pixman-devel libaio-devel
```

## FAQ

#### qemu: could not load PC BIOS 'bios-256k.bin'

谷歌解决
https://techglimpse.com/qemu-system-x86-command-error-solution/
```
ls -l /usr/share/qemu/bios.bin
find /usr -name bios.bin
使用qemu的时候，加一个-L即可
或者对bios.bin做一个软链接
或者编译configure的时候加上参数, --firmwarepath=/usr/share/qemu-kvm/
```

## 参考资料

[Compile qemu on Ubuntu 20.04](https://bevisy.github.io/p/compile-qemu-on-ubuntu-20.04/)
