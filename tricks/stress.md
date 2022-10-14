# stress用法

## 安装

#### 源码安装

https://github.com/resurrecting-open-source-projects/stress
```
git clone https://github.com/resurrecting-open-source-projects/stress
cd stress
./autogen.sh
./configure
make
make install
```

## 内存测试

http://blog.lujun9972.win/blog/2018/05/06/%E4%BD%BF%E7%94%A8stress%E8%BF%9B%E8%A1%8C%E5%8E%8B%E5%8A%9B%E6%B5%8B%E8%AF%95/

使用 stress -m N 会让stress生成N个工作进程来占用内存。每个进程默认占用256M内存，但可以通过 --vm-bytes 来进行设置。 例如
```
stress -m 3 --vm-bytes 300M
stress  --vm 4  --vm-bytes  1024M  --vm-keep
```


http://blog.lujun9972.win/blog/2021/04/16/%E5%9C%A8linux%E4%B8%8B%E5%88%9B%E5%BB%BA%E5%86%85%E5%AD%98%E7%A3%81%E7%9B%98%E7%9A%84%E4%B8%8D%E5%90%8C%E6%96%B9%E6%B3%95%E5%8F%8A%E5%8C%BA%E5%88%AB/index.html

或者直接mount内存到目录, 拷贝文件过来
(但是这样cache内存显示增加了...)
```
# 使用tmpfs或者ramfs(区别是ramfs是纯内存)
#mount tmpfs -t tmpfs -o size=1G -o mode=1777 /mnt/
mount -t ramfs -o size=7G ramfs /mnt
dd if=/dev/zero of=adam.bin bs=1M count=6500
```

## cpu测试

使用 stress -c N 会让stress生成N个工作进程进行开方运算，以此对CPU产生负载。

比如你的CPU有四个核，那么可以运行
```
stress -c 4
```
