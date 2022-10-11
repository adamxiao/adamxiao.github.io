# strace用法

我的常用命令:
```
strace -o /tmp/adam.strace.log -f -s 8000 -tt -T -p 1234
```

* -f 表示跟踪子进程
* -s 8000表示参数长度
* -tt 表示时间详细显示
* ...

#### strace exclude syscall

only syscall `-e sendto`
exclude  syscall `-e 'trace=!epoll_wait,select'`
或者 `-e trace=\!select` (使用反斜杠处理)
