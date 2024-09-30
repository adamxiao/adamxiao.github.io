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

#### strace threads

[strace追踪多线程程序](https://blog.csdn.net/prike/article/details/50224193)

方法一
先用ps -mp pid或者top -H查出线程pid。

然后strace -p pid追踪其中一个线程。

方法二
直接用strace -fp pid追踪进程下所有线

## 参考资料

[Linux调试分析诊断利器——strace](https://www.cnblogs.com/clover-toeic/p/3738156.html)
