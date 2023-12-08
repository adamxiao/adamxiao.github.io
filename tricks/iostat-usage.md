# iostat使用方法

iostat -d -x -k -N 60 2
```
nvme0c33n1        0.00     1.20   67.23   60.80   374.07   766.41    17.82     0.00    0.08    0.09    0.07   0.05   0.58
sdg               0.00     0.00    0.57   11.03     2.75   110.90    19.59     0.01    1.02    0.82    1.03   0.38   0.45
```

参数解析
- `-d`: 表示磁盘
- `-x`: 显示详细信息
- `-k`: 以 KB 为单位显示
- `-N`： 显示磁盘阵列(LVM) 信息
最后接上时间间隔，次数

## FAQ

#### nvme磁盘io统计数据问题

iostat统计出来的device-name不匹配!!!
```
nvme0c33n1        0.00     1.20   67.23   60.80   374.07   766.41    17.82     0.00    0.08    0.09    0.07   0.05   0.58
```

使用iostat统计
```
$mount | grep ssd113
/dev/nvme0n1 on /home/kylin-data/ssd113 type ext4 (rw,relatime)

$iostat -d -x -k -N 60 2 /dev/nvme0n1
Linux 4.19.90-2003.4.0.0036.ky3.kb29.ksvd2.x86_64 (node8)       12/04/2023      _x86_64_        (48 CPU)

Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
nvme0n1           0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00

Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
nvme0n1           0.00     0.00    0.00    0.00     0.00     0.00     0.00     0.00    0.00    0.00    0.00   0.00   0.00
```

https://bugs.launchpad.net/curtin/+bug/1830913
```
/sys/class/block/nvme0c33n1
```
