# linux命令行工具使用

记录一些常用的linux命令行工具的使用

ps 命令查看进程启动的精确时间和启动后所流逝的时间
```
ps -eo pid,lstart,etime,cmd | grep nginx
16968 Fri Mar  4 16:04:27 2016 41-21:14:04 nginx: master process /usr/sbin/nginx
```

《dd status progress》
[How to Use DD Show Progress Command in Linux?](https://phoenixnap.com/kb/dd-show-progress)

需要dd版本不低于8.24
```
dd if=/path/to/input of=/path/to/output status=progress
```

另外一种方法，使用pv获取进度
```
sudo apt install pv
sudo yum install pv
dd if=/path/to/input | pv | dd of=/path/to/output
```

还有就是以前的老方法, 发信号给dd进程:
```
# On Linux:
sudo kill -USR1 $(pgrep ^dd)
# On OSX/BSD:
sudo kill -INFO $(pgrep ^dd) # (on OSX)

watch -n5 'sudo kill -USR1 $(pgrep ^dd)'
```
