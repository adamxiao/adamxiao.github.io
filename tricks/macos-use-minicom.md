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

## iterm使用串口

关键字《iterm 配置串口》

https://blog.csdn.net/hao_zhang_shrek/article/details/102958520

```
screen /dev/cu.usbserial-1430 9600 -L
```

接入普通tc盒子，没有任何反应

接入ft2000机器，报错

