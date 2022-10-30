# strace用法

我的常用命令:
```
strace -o /tmp/adam.strace.log -f -s 8000 -tt -T -p 1234
```

* -f 表示跟踪子进程
* -s 8000表示参数长度
* -tt 表示显示时间戳信息, tt表示详细显示
* ...

* -T 表示在输出结果中加上系统调用的耗时信息
* -p 输出指定进程的结果
* -e 表示只输出网络相关和 close() 系统调用的日志
  -e trace=network,close
* -o 表示将输出结果存储到指定文件中

#### strace exclude syscall

only syscall `-e sendto`
exclude  syscall `-e 'trace=!epoll_wait,select'`
或者 `-e trace=\!select` (使用反斜杠处理)
