# macos使用minicom串口

## minicom安装

```
brew install minicom
```


## 使用minicom

关键字《macbook minicom使用》

[Minicom---MAC OS使用串口调试交换机的利器](https://www.jianshu.com/p/3d921b547705)

TODO: 补充图片

```
# 获取usb串口信息
ls /dev/ | grep usb
```

* 配置minicom使用串口设备，以及波特率

命令行启动minicom的参数
```
minicom -D /dev/ttyS0 -b 115200 -8
minicom -D /dev/ttyS0 -b 115200 -8 -w -c on -R utf8
```

* -w: 启动minicom的时候，开启自动换行：
如果不加这个项，那么在minicom和pc交互的时候中键入命令超过一行时候会被截断，（这时候可以通过<C-a> w来开和关切换截断行功能）.

* -c on: 启动minicom的时候，显示颜色：
这样，启动之后我们会发现显示的内容不是黑白的了。

=> 接入华为交换机, 只有输出, 无法输入, 发现minicom的`Hardware Flow Control` 默认为Yes导致的
`Ctrl-A o` -> `Serial port setup` 配置这个参数
华为交换机默认**无流控**，但若终端启用了流控（如RTS/CTS），会阻塞输入：

- Hardware Flow Control: No
- Software Flow Control: No


华为交换机参数
```
minicom -D /dev/ttyUSB0 -b 9600 -8
```

- 波特率: 9600
- 数据位: 8
- 停止位: 1
- 奇偶校验: 无
- 流控制: 无

#### 华为交换机配置

配置trunk, access口
```
system-view
interface GigabitEthernet 0/0/19
display this

port-security
port-isolate
port-mirroring

port link-type trunk
port trunk allow-pass vlan 2 100

port link-type access
port default vlan 2

quit
```

#### 华为S5700交换机重置出厂设置

重置密码, 问AI得到答案验证ok

- 1.重启设备进入BootROM
  - 交换机上电启动时，当出现"Press Ctrl+B to enter BootROM"提示时，3秒内按下Ctrl+B
  - 输入默认密码：Admin@huawei.com（注意大小写）
- 2.清除配置文件
  输入 7. Clear Configuration File
- 3.恢复启动
  输入 1. Boot with default mode

## iterm使用串口

关键字《iterm 配置串口》

https://blog.csdn.net/hao_zhang_shrek/article/details/102958520

```
screen /dev/cu.usbserial-1430 9600 -L
```

接入普通tc盒子，没有任何反应

接入ft2000机器，报错

