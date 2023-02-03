# ky coreos iso镜像制作

## 构建iso步骤

- 1.配置目录树创建
```
mkdir -p srv/{builds,cache,src/config}
```

- 2.解压coreos配置文件
```
tar -xzf ~/coreos-assembler-config.tar.gz -C srv/src/config/
```

- 3.运行coreos镜像制作容器
```
docker run --dns 223.5.5.5 --rm -ti --security-opt label=disable \
  --user root  --entrypoint /bin/bash --privileged -v $PWD/srv:/srv/ \
  --device /dev/kvm --device /dev/fuse --tmpfs /tmp -v /var/tmp:/var/tmp \
  --name cosa --entrypoint /bin/bash hub.iefcu.cn/xiaoyun/coreos-assembler:1115
```

- 3.准备工作

```
(cd srv/src/config/ && git init && git add .) # 需要git init
git commit -m "init"
cosa fetch # 拉取相关资源
```

- 5.最后构建iso镜像
```
cosa build ostree metal metal4k && cosa buildextend-live # 构建iso和tar包
cosa build ostree  # 只构建coreos tar包
```

## 参考资料

TODO:

- 怎么制作构建镜像的容器镜像coreos-assembler的?
- 一定要qemu环境才行吗?
- 如何修改里面的rpm包等

这个进程使用了qemu做事情
```
[root@6ee6a06f7dad srv]# ps -ef
UID        PID  PPID  C STIME TTY          TIME CMD
root         1     0  0 06:39 pts/0    00:00:00 /bin/bash
root       273     1  0 06:53 pts/0    00:00:00 bash /usr/lib/coreos-assembler/cmd-build ostree metal metal4k
root     17043     0  0 06:59 pts/1    00:00:00 bash
root     17147   273  0 07:00 pts/0    00:00:00 bash /usr/lib/coreos-assembler/cmd-buildextend-metal4k
root     17404 17147  0 07:00 pts/0    00:00:00 kola qemuexec -m 2048 --auto-cpus -U --workdir none --console-to-file /srv/tmp/build.metal4k/runvm-console.txt -- -drive if=none,id=root,format=raw,snapsho
root     17416 17404 99 07:00 pts/0    00:01:36 qemu-system-aarch64 -machine virt,accel=kvm,gic-version=max -cpu host -m 2048 -smp 16 -object rng-random,filename=/dev/urandom,id=rng0 -device virtio-rng-p
root     17496 17043  0 07:00 pts/1    00:00:00 ps -ef
```
