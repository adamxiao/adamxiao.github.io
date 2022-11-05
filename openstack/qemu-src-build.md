# 源码编译qemu

## ubuntu编译

```
git clone https://git.qemu.org/git/qemu.git
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

## 参考资料

[Compile qemu on Ubuntu 20.04](https://bevisy.github.io/p/compile-qemu-on-ubuntu-20.04/)
