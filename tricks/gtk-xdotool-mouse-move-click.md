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
