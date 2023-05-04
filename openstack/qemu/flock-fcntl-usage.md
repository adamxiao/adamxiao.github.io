# flock 和 fcntl 使用

关键字《flock 获取锁状态》

## 共享存储flock

[flock v.s. fcntl](https://www.jianshu.com/p/a4ea27c6ed1f)

关键字《共享存储flock》
https://www.cnblogs.com/wiseo/p/14884187.html
```
flock -x flock.lock -c 'sleep 30'
flock -s flock.lock -c 'echo hello' 
gluster
系统调用居然全是flock
不支持文件锁，则会输出以下内容，此时应检查服务端是否支持文件锁、客户端nfs挂载协议版本
flock:没有可用的锁
```

```
import fcntl
path='flock.lock'
lockfile = open(path, 'a')
fcntl.lockf(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
fcntl.lockf(lockfile, fcntl.LOCK_UN)
```

对应系统调用是
```
fcntl(3, F_SETLK, {l_type=F_WRLCK, l_whence=SEEK_SET, l_start=0, l_len=0}) = 0 <0.000934>
fcntl(3, F_SETLKW, {l_type=F_UNLCK, l_whence=SEEK_SET, l_start=0, l_len=0}) = 0 <0.000834>
另外一个程序获取锁失败
fcntl(3, F_SETLK, {l_type=F_WRLCK, l_whence=SEEK_SET, l_start=0, l_len=0}) = -1 EAGAIN (Resource temporarily unavailable) <0.000890>
```

[Linux 下三种文件锁 —— fcntl/lockf、flock](https://www.jianshu.com/p/643cbd96a00c)
Posix locks: fcntl/lockf => 不支持 ocfs2, flock 支持ocfs2
fcntl 支持glusterfs, qemu镜像用的是fcntl


## qemu使用fcntl问题

- qemu是怎么使用fcntl加锁的?
  raw_check_perm -> raw_handle_perm_lock -> raw_check_lock_bytes? => 就是这个加锁
  raw_set_perm -> raw_apply_lock_bytes => 这个貌似是解锁

最终调用命令
```
7826  09:08:42.919800 fcntl(10, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=100, l_len=1}) = 0 <0.000652>
7826  09:08:42.920472 fcntl(10, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=101, l_len=1}) = 0 <0.000608>
7826  09:08:42.921099 fcntl(10, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=103, l_len=1}) = 0 <0.000723>
7826  09:08:42.921840 fcntl(10, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=201, l_len=1}) = 0 <0.000661> => bad?
7826  09:08:42.922521 fcntl(10, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=203, l_len=1}) = 0 <0.000603> 
```

- qemu是怎么检测到锁冲突的?
  其实问题是，为什么可以锁上，然后再检测锁失败?
  => 写一段代码进行测试验证, 发现锁上使用读锁，检查使用写锁(互斥)
  (A进程可以读锁定，写锁检测也正常，B进程可以读锁定，但是写锁检测失败!)

```
write(1, "qemu_lock_fd_test exclusive is 1, fd is 10, off 201, ret 0\n", 59) = 59 <0.000013>
write(1, "raw_check_lock_bytes qemu_lock_fd_test write off 201 failed, ret=-11\n", 69) = 69 <0.000012> 
```

#### raw_check_perm接口

问题:
- 为什么我加日志，有些check_perm感觉没有做事情?
  貌似会被调用很多次, 参数略有不同导致?
  => 可能如下: 1.权限相同，不需要修改权限; (share权限默认是31, BLK_PERM_ALL 0x1f)

作用: 检查权限?
属于(.bdrv_check_perm), 被block.c的相关接口调用

```
static int raw_check_perm(BlockDriverState *bs, uint64_t perm, uint64_t shared,
                          Error **errp)
{
    BDRVRawState *s = bs->opaque;
    BDRVRawReopenState *rs = NULL;
```

逻辑:
- 检查 s->perm_change_fd ?
- 可能生成s->perm_change_fd
  根据s->reopen_state状态来
- raw_handle_perm_lock(RAW_PL_PREPARE)
  准备权限
- raw_apply_lock_bytes(s->perm_change_fd != 0)
  拷贝权限到新的fd上

#### raw_set_perm接口

问题:
- 跟raw_check_perm的区别是什么呢，感觉raw_check_perm也会设置权限?
  => 区别应该是解锁权限! op = RAW_PL_COMMIT

作用: 设置权限? 解锁权限吧!
属于(.bdrv_set_perm), 被block.c的相关接口调用

逻辑
- 处理s->perm_change_fd = 0;
- 调用raw_handle_perm_lock处理权限(RAW_PL_COMMIT)

#### static raw_handle_perm_lock

主要是调用raw_apply_lock_bytes吧?

被如下三个接口调用的
**raw_check_perm**, raw_set_perm, raw_abort_perm_update
RAW_PL_PREPARE等,  RAW_PL_COMMIT, RAW_PL_ABORT


逻辑:
- 调用raw_apply_lock_bytes
  加读锁
- **成功则调用 raw_check_lock_bytes 检查权限**
  使用写锁检测

#### static raw_apply_lock_bytes

逻辑: 真正处理权限的逻辑
=> 就是调用fnctl加锁

#### qemu

```
raw_check_perm begin fd is /home/kylin-ksvd/xiaoyun/centos-ksvd2020.qcow2,perm_change_fd: 0,reopen_state: 0, 0, 31
raw_handle_perm_lock fd 10, 0, 31
raw_set_perm fd 10, 0, 31
raw_handle_perm_lock fd 10, 0, 31
raw_apply_lock_bytes fd 10 write perm is 0, share_perm is 18446744073709551584, unlock 1
raw_check_perm begin fd is /home/kylin-ksvd/xiaoyun/centos-ksvd2020.qcow2,perm_change_fd: 0,reopen_state: 0, 11, 21
raw_handle_perm_lock fd 10, 11, 21
raw_apply_lock_bytes fd 10 write perm is 11, share_perm is 18446744073709551594, unlock 0
raw_handle_perm_lock raw_apply_lock_bytes lock sucess, start check, fd 10, 11, 21
raw_check_lock_bytes fd 10 write perm is 11, share_perm is 21
really raw_check_perm fd is 11, 11, 21
raw_apply_lock_bytes fd 11 write perm is 11, share_perm is 18446744073709551594, unlock 0
raw_set_perm fd 11, 11, 21
raw_handle_perm_lock fd 11, 11, 21
raw_apply_lock_bytes fd 11 write perm is 11, share_perm is 18446744073709551594, unlock 1
raw_check_perm begin fd is /home/kylin-ksvd/xiaoyun/centos-ksvd2020.qcow2,perm_change_fd: 0,reopen_state: 0, 11, 21
raw_handle_perm_lock fd 11, 11, 21
raw_set_perm fd 11, 11, 21
raw_handle_perm_lock fd 11, 11, 21
raw_apply_lock_bytes fd 11 write perm is 11, share_perm is 18446744073709551594, unlock 1
raw_check_perm begin fd is /home/kylin-ksvd/xiaoyun/centos-ksvd2020.qcow2,perm_change_fd: 0,reopen_state: 0, 11, 21
raw_handle_perm_lock fd 11, 11, 21
raw_set_perm fd 11, 11, 21
raw_handle_perm_lock fd 11, 11, 21
raw_apply_lock_bytes fd 11 write perm is 11, share_perm is 18446744073709551594, unlock 1
raw_check_perm begin fd is /home/kylin-ksvd/xiaoyun/centos-ksvd2020.qcow2,perm_change_fd: 0,reopen_state: 0, 11, 21
raw_handle_perm_lock fd 11, 11, 21
raw_set_perm fd 11, 11, 21
raw_handle_perm_lock fd 11, 11, 21
raw_apply_lock_bytes fd 11 write perm is 11, share_perm is 18446744073709551594, unlock 1

^Cqemu-system-x86_64: terminating on signal 2
raw_check_perm begin fd is /home/kylin-ksvd/xiaoyun/centos-ksvd2020.qcow2,perm_change_fd: 0,reopen_state: 0, 11, 21
raw_handle_perm_lock fd 11, 11, 21
raw_set_perm fd 11, 11, 21
raw_handle_perm_lock fd 11, 11, 21
raw_apply_lock_bytes fd 11 write perm is 11, share_perm is 18446744073709551594, unlock 1
raw_check_perm begin fd is /home/kylin-ksvd/xiaoyun/centos-ksvd2020.qcow2,perm_change_fd: 0,reopen_state: 0, 0, 31
raw_handle_perm_lock fd 11, 0, 31
really raw_check_perm fd is 16, 0, 31
raw_apply_lock_bytes fd 16 write perm is 0, share_perm is 18446744073709551584, unlock 0
raw_set_perm fd 16, 0, 31
raw_handle_perm_lock fd 16, 0, 31
raw_apply_lock_bytes fd 16 write perm is 0, share_perm is 18446744073709551584, unlock 1
```

#### fcntl加锁

关键字《xxx》

https://xy2401.com/local-docs/gnu/manual.zh/libc/Open-File-Description-Locks.html

[linux中fcntl()、lockf、flock的区别](https://developer.aliyun.com/article/515873)

通过函数参数功能可以看出fcntl是功能最强大的，它既支持共享锁又支持排他锁，即可以锁住整个文件，又能只锁文件的某一部分。

qemu-kvm中的fcntl使用
```
fcntl(10, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=100, l_len=1}) = 0 <0.000013>
fcntl(10, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=201, l_len=1}) = 0 <0.000009>
fcntl(10, F_OFD_GETLK, {l_type=F_UNLCK, l_whence=SEEK_SET, l_start=200, l_len=1, l_pid=0}) = 0 <0.000008>
fcntl(10, F_OFD_GETLK, {l_type=F_UNLCK, l_whence=SEEK_SET, l_start=201, l_len=1, l_pid=0}) = 0 <0.000045>

fcntl(11, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=100, l_len=1}) = 0 <0.000011>
fcntl(11, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=101, l_len=1}) = 0 <0.000010>
fcntl(11, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=103, l_len=1}) = 0 <0.000010>
fcntl(11, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=201, l_len=1}) = 0 <0.000009>
fcntl(11, F_OFD_SETLK, {l_type=F_RDLCK, l_whence=SEEK_SET, l_start=203, l_len=1}) = 0 <0.000010>
```

#### F_OFD_GETLK

关键字《F_OFD_GETLK 用法》

https://xy2401.com/local-docs/gnu/manual.zh/libc/Open-File-Description-Locks.html

fcntl (filedes, F_OFD_GETLK, lockp)

如果已经有一个锁，它将阻塞lockp参数，有关该锁的信息被写入*lockp 。如果现有锁与按指定进行新锁兼容，则不会报告这些锁。因此，您应该指定一种锁定类型F_WRLCK如果您想了解读和写锁，或者F_RDLCK如果您只想了解写锁定。

可能有一个以上的锁影响到由lockp争论，但是fcntl仅返回有关其中之一的信息。在这种情况下返回的锁是不确定的。

的l_whence的成员lockp结构设置为SEEK_SET和l_start和l_len字段设置为标识锁定区域。

如果不存在冲突的锁，则唯一更改为lockp结构是更新l_type值字段F_UNLCK 。

[(好)Linux Lock - flock and fcntl](https://www.jianshu.com/p/8b355893f709)
OFD(Open File Descriptor) ：第一次打开文件时候，在内核创建一个OFD。如果不同进程打开同一个文件，不同的fd会对应同一个内核态的open fd。

flock和fcntl在内核中都用`struct file_lock`实现。其主要差别就在于owner的不同。如果lock的owner相同，conflict的检测就会跳过，即相同owner的lock可以递归申请。

#### flock加锁

- 关于flock函数，首先要知道flock函数只能对整个文件上锁，而不能对文件的某一部分上锁，这是于fcntl/lockf的第一个重要区别，后者可以对文件的某个区域上锁。其次，flock只能产生劝告性锁。

- 使用open两次打开同一个文件，得到的两个fd是独立的（因为底层对应两个file对象），
  通过其中一个加锁，通过另一个无法解锁，并且在前一个解锁前也无法上锁。测试程序如程序三：

```
#include stdio.h>
#include unistd.h>
#include stdlib.h>
#include sys/file.h>
int main (int argc, char ** argv)
{
    int ret;
    int fd1 = open("./tmp.txt",O_RDWR);
    int fd2 = open("./tmp.txt",O_RDWR);
    printf("fd1: %d, fd2: %d\n", fd1, fd2);
    ret = flock(fd1,LOCK_EX);
    printf("get lock1, ret: %d\n", ret);
    ret = flock(fd2,LOCK_EX);
    printf("get lock2, ret: %d\n", ret);
    return 0;
}
```

输出结果如下:
```
fd1: 3, fd2: 4
get lock1, ret: 0
get lock2, ret: -1
```

- int flock(int fd, int operation);  // Apply or remove an advisory lock on the open file specified by fd，只是建议性锁

  其中fd是系统调用open返回的文件描述符，operation的选项有：

- LOCK_SH ：共享锁
- LOCK_EX ：排他锁或者独占锁
- LOCK_UN : 解锁。
- LOCK_NB：非阻塞（与以上三种操作一起使用）

#### ocfs2不支持fcntl锁

关键字《ocfs2不支持fcntl锁》

https://www.jianshu.com/p/643cbd96a00c

## 两种锁的关系

- 关于flock函数，首先要知道**flock函数只能对整个文件上锁，而不能对文件的某一部分上锁**，这是于fcntl/lockf的第一个重要区别，后者可以对文件的某个区域上锁。其次，**flock只能产生劝告性锁**。

https://www.jianshu.com/p/643cbd96a00c
- linux 2.0 后在本地文件系统上互不影响
- 在 NFS 上， flock 由于底层实现仿造 fcntl 的字节范围锁，所以两者会产生交互。

测试发现在glusterfs(nfs也一样)文件系统上, flock影响了fnctl锁
```
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>
#include <sys/file.h>
#include <stdio.h>
#include <errno.h>
#include <stdbool.h>

#define F_OFD_GETLK 36
#define F_OFD_SETLK 37

static int qemu_lock_fcntl(int fd, int64_t start, int64_t len, int fl_type)
{
    int ret;
    struct flock fl = {
        .l_whence = SEEK_SET,
        .l_start  = start,
        .l_len    = len,
        .l_type   = fl_type,
    };
    do {
        ret = fcntl(fd, F_OFD_SETLK, &fl);
    } while (ret == -1 && errno == EINTR);
    return ret == -1 ? -errno : 0;
}

int qemu_lock_fd_test(int fd, int64_t start, int64_t len, bool exclusive)
{
    int ret;
    struct flock fl = {
        .l_whence = SEEK_SET,
        .l_start  = start,
        .l_len    = len,
        .l_type   = exclusive ? F_WRLCK : F_RDLCK,
    };
    // 获取锁状态, 如果不是解锁状态，则返回错误
    printf("qemu_lock_fd_test begin fd is %d, off %ld:%ld\n", fd, fl.l_start, fl.l_len);
    ret = fcntl(fd, F_OFD_GETLK, &fl);
    if (ret != 0 || fl.l_type != F_UNLCK) {
        printf("[ERR]qemu_lock_fd_test end fd is %d, off %ld:%ld\n", fd, fl.l_start, fl.l_len);
    }
    if (ret == -1) {
        return -errno;
    } else {
        return fl.l_type == F_UNLCK ? 0 : -EAGAIN;
    }
}

int lock_fd(int fd)
{
    int ret = 0;
    int64_t off[5] = {100,101,103,201,203};
    int i;
    for (i = 0; i < 5; i++) {
        ret = qemu_lock_fcntl(fd, off[i], 1, F_RDLCK);
        if (0 != ret) {
            printf("lock failed\n");
            return -1;
        }
    }

    return 0;
}

int check_fd(int fd)
{
    int ret = 0;
    bool exclusive = true;

    int64_t off[5] = {200,201,203,101,103};
    int i;
    for (i = 0; i < 5; i++) {
        ret = qemu_lock_fd_test(fd, off[i], 1, exclusive);
        if (0 != ret) {
            printf("lock test failed\n");
            return -1;
        }
    }
    return 0;
}

int main(int argc, char *argv[])
{
    int ret = 0;
    int fd = open("./tmp.txt",O_RDWR);
    int newfd = open("./tmp.txt",O_RDWR);

    ret = lock_fd(fd);
    if (ret != 0) {
        return -1;
    }

    ret = check_fd(fd);
    if (ret != 0) {
        return -1;
    }

    flock(fd, LOCK_EX|LOCK_NB);
    flock(fd, LOCK_UN);

    // qemu中切换到新fd上加锁
    flock(newfd, LOCK_EX|LOCK_NB);

    ret = lock_fd(newfd);
    if (ret != 0) {
        return -1;
    }

    close(fd); // 关闭旧fd

    sleep(100);

    return 0;
}
```

两个主机进程运行，另外一个报错
```
qemu_lock_fd_test begin fd is 3, off 200:1
[ERR]qemu_lock_fd_test end fd is 3, off 104:97
lock test failed
```

#### 其他

=> TODO: 在glusterfs共享文件系统中，有影响? => 有!

那么flock和lockf/fcntl所上的锁有什么关系呢？答案时互不影响。测试程序如下：

```
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/file.h>
int main(int argc, char **argv)
{
    int fd, ret;
    int pid;
    fd = open("./tmp.txt", O_RDWR);
    ret = flock(fd, LOCK_EX);
    printf("flock return ret : %d\n", ret);
    ret = lockf(fd, F_LOCK, 0);
    printf("lockf return ret: %d\n", ret);
    sleep(100);
    return 0;
}
```

#### 验证fcntl的set，get

摘自qemu源码, 略微改动验证
```
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>
#include <sys/file.h>
#include <stdio.h>
#include <errno.h>
#include <stdbool.h>

#define F_OFD_GETLK 36
#define F_OFD_SETLK 37

static int qemu_lock_fcntl(int fd, int64_t start, int64_t len, int fl_type)
{
    int ret;
    struct flock fl = {
        .l_whence = SEEK_SET,
        .l_start  = start,
        .l_len    = len,
        .l_type   = fl_type,
    };
    do {
        ret = fcntl(fd, F_OFD_SETLK, &fl);
    } while (ret == -1 && errno == EINTR);
    return ret == -1 ? -errno : 0;
}

int qemu_lock_fd_test(int fd, int64_t start, int64_t len, bool exclusive)
{
    int ret;
    struct flock fl = {
        .l_whence = SEEK_SET,
        .l_start  = start,
        .l_len    = len,
        .l_type   = exclusive ? F_WRLCK : F_RDLCK,
    };
    // 获取锁状态, 如果不是解锁状态，则返回错误
    ret = fcntl(fd, F_OFD_GETLK, &fl);
    if (ret != 0 || fl.l_type != F_UNLCK) {
        printf("[ERR]qemu_lock_fd_test failed, exclusive is %d, fd is %d, off %ld, ret %d\n", exclusive, fd, start, ret);
    }
    if (ret == -1) {
        return -errno;
    } else {
        return fl.l_type == F_UNLCK ? 0 : -EAGAIN;
    }
}

int main(int argc, char *argv[])
{
    int ret = 0;
    int fd = open("./tmp.txt",O_RDWR);
    bool exclusive = true;
    int64_t off = 201;
    int64_t len = 1;

    ret = qemu_lock_fcntl(fd, off, len, F_RDLCK);
    if (0 != ret) {
        printf("lock failed\n");
        return -1;
    }

    ret = qemu_lock_fd_test(fd, off, len, exclusive);
    if (0 != ret) {
        printf("lock test failed\n");
        return -2;
    }

    sleep(100);

    return 0;
}
```
