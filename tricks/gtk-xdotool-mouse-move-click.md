# 使用xdotool等工具自动操作鼠标

自动判定当前窗口是否XXX, 然后移动鼠标，点击鼠标
```
#!/bin/bash

while /bin/true;
do
    active_window=`xdotool getactivewindow`
    if xwininfo -id $active_window | grep -q "KSVD Client" 2>/dev/null ; then
        echo "udap client closed, connect again"
        xdotool mousemove 1860 250 && xdotool click 1
        sleep 20
    fi
done
```

VDE R022C27 配置使用自动化

安装xdotool => xdotool-3.20150503.1-1.el7.x86_64.rpm
http://10.20.20.17/koji/buildinfo?buildID=18330

然后使用kylin用户, export DISPLAY=:0, 就可以使用xdotool工具自动化处理了!
