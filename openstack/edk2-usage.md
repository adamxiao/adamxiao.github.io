# edk2编译使用

克隆源码编译
```
git clone https://github.com/tianocore/edk2.git
cd edk2/
git submodule update --init
source edksetup.sh
make -C BaseTools
build -p OvmfPkg/OvmfPkgX64.dsc -a X64 -t GCC5 -b DEBUG -DFD_SIZE_2MB -DDEBUG_ON_SERIAL_PORT=TRUE -n $(nproc)
```
=> 注意这里的GCC5? 用gcc 4.8.5是不行的
=> nasm 版本有兼容性问题...

安装依赖
```
apt install uuid-dev nasm binutils
yum install libuuid-devel
```

=> 编译环境有问题，暂时用别人构建好的容器编译好了
```
hub.iefcu.cn/dev_builders/voi-uefi
```
