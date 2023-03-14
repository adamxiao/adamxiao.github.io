# linux命令行工具使用

记录一些常用的linux命令行工具的使用

ps 命令查看进程启动的精确时间和启动后所流逝的时间
```
ps -eo pid,lstart,etime,cmd | grep nginx
16968 Fri Mar  4 16:04:27 2016 41-21:14:04 nginx: master process /usr/sbin/nginx
```
