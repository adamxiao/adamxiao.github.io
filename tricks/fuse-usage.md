# fuse开发使用

## 接口使用

#### readdir

支持list文件目录, 详见示例

```
int hello_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
                         off_t offset, struct fuse_file_info *fi, enum fuse_readdir_flags flags) {
```

返回文件列表，会回调这个函数
```
typedef int (*fuse_fill_dir_t) (void *buf, const char *name,
                const struct stat *stbuf, off_t off,
                enum fuse_fill_dir_flags flags);
```

#### getattr

获取文件属性: 大小, 权限, 类型(目录，链接?)等
=> 类似stat 文件

```
int hello_getattr(const char *path, struct stat *stbuf, struct fuse_file_info *fi)
```

返回信息，会填充到stat输出参数中

#### utimens

更新时间戳, 例如touch文件

```
int hello_utimens(const char *path, const struct timespec tv[2], struct fuse_file_info *fi)
```

- 必须先open, 才能touch

#### unlink

删除文件

```
int hello_unlink(const char *path)
```

#### open

打开文件

```
int hello_open(const char *path, struct fuse_file_info *fi)
```

#### create

应用层创建文件时调用?

```
int hello_create(const char *path, mode_t mode, struct fuse_file_info *fi)
```

=> 就是读写创建open文件
```
openat(AT_FDCWD, "/mnt/hellofs/adam3", O_WRONLY|O_CREAT|O_EXCL, 0644)
```

#### read

读文件内容

```
int hello_read(const char *path, char *buf, size_t size, off_t offset, struct fuse_file_info *fi)
```

- 必须先open, 才能读

#### write

写文件内容

```
int hello_write(const char *path, const char *buf, size_t size, off_t offset, struct fuse_file_info *fi)
```

限制条件

- 必须先写模式open文件

#### truncate

截断文件

```
int hello_truncate(const char *path, off_t size, struct fuse_file_info *fi) {
```

限制条件

- 必须先写模式open文件

#### chmod

修改属组接口，暂不支持, 测试用例脚本调用了而已

## 测试用例

生成一个文件
- 随机读写
  检查每次读的内容;
  检查最终文件内容;

gpt生成测试用例脚本
```
写一个测试用例，首先拷贝一个文件A，到另一个位置B，到另外一个位置C，然后开始进行如下的测试：
对文件B和文件C进行相同的随机读写，每次比较读取到的内容是否相同，以及写入之后，对比文件md5值是否相同。随机读写的offset范围限定在100MB以内,大小限定在1MB以内。

再次读取写入的内容，对比内容是否相同，去除掉整个文件的md5值的比较
```

- truncate大小
  检查文件内容
  => 属于底层的接口, 暂没必要测

## 简单示例

gpt《能不能将redis二进制string，map成一个块设备文件》
《怎么实现fuse文件系统》

```
sudo apt install fuse3 libfuse3-dev
sudo apt install pkg-config gcc cmake make
```

makefile
```
all:
        gcc -Wall -D_FILE_OFFSET_BITS=64 -o hellofs hellofs.c `pkg-config fuse3 --cflags --libs`
test:
        #mkdir -p /mnt/hellofs
        ./hellofs /mnt/hellofs
clean:
        fusermount -u /mnt/hellofs
```

简单的一个hello, fuse示例
```
#define FUSE_USE_VERSION 31

#include <fuse.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>

// 文件系统中的文件内容
const char *hello_content = "Hello, FUSE!\n";

// 获取文件属性
static int hello_getattr(const char *path, struct stat *stbuf, struct fuse_file_info *fi) {
    (void) fi; // unused

    memset(stbuf, 0, sizeof(struct stat));
    if (strcmp(path, "/") == 0) {
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
    } else if (strcmp(path, "/hello") == 0) {
        stbuf->st_mode = S_IFREG | 0444;
        stbuf->st_nlink = 1;
        stbuf->st_size = strlen(hello_content);
    } else {
        return -ENOENT;
    }

    return 0;
}

// 读取目录
static int hello_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
                         off_t offset, struct fuse_file_info *fi, enum fuse_readdir_flags flags) {
    (void) offset;
    (void) fi;
    (void) flags; // unused

    if (strcmp(path, "/") != 0)
        return -ENOENT;

    struct stat st;
    memset(&st, 0, sizeof(st));

    st.st_ino = 1;
    st.st_mode = S_IFDIR | 0755;
    filler(buf, ".", &st, 0, 0);

    st.st_ino = 2;
    st.st_mode = S_IFDIR | 0755;
    filler(buf, "..", &st, 0, 0);

    st.st_ino = 3;
    st.st_mode = S_IFREG | 0444;
    st.st_size = strlen(hello_content);
    filler(buf, "hello", &st, 0, 0);

    return 0;
}

// 打开文件
static int hello_open(const char *path, struct fuse_file_info *fi) {
    if (strcmp(path, "/hello") != 0)
        return -ENOENT;

    return 0;
}

// 读取文件
static int hello_read(const char *path, char *buf, size_t size, off_t offset,
                      struct fuse_file_info *fi) {
    if (strcmp(path, "/hello") != 0)
        return -ENOENT;

    size_t len = strlen(hello_content);
    if (offset >= len)
        return 0;

    size_t copy_len = len - offset;
    if (copy_len > size)
        copy_len = size;

    memcpy(buf, hello_content + offset, copy_len);
    return copy_len;
}

// FUSE操作表
static struct fuse_operations hello_oper = {
    .getattr = hello_getattr,
    .readdir = hello_readdir,
    .open = hello_open,
    .read = hello_read,
};

int main(int argc, char *argv[]) {
    return fuse_main(argc, argv, &hello_oper, NULL);
}
```

## FAQ

#### 普通用户访问文件

- 1.原始目录权限处理
=> 不用处理
```
chmod 755 /mnt/hellofs
```
- 2.fuse挂载权限配置
```
./hellofs /mnt/hellofs -o allow_other -o default_permissions -d -o uid=1000
# -o allow_other：允许其他用户访问文件系统。
# -o default_permissions：使用系统的权限检查机制。
# -o uid=1000 : 设置挂载后的用户, fuse文件系统里面所有的文件都是这个
# -o gid=1000 : 设置挂在后的属组
```
- 3.fuse应用权限配置
=> 改了用户后，这个也不需要
```
hello_getattr 中输出对应的权限
stbuf->st_mode = S_IFDIR | 0755;
```

#### 调试使用

有参数，可以前端运行，开启调试日志
```
./hellofs -d /mnt/hellofs
```

