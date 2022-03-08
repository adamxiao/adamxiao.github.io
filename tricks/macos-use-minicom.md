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


## iterm使用串口

关键字《iterm 配置串口》

https://blog.csdn.net/hao_zhang_shrek/article/details/102958520

```
screen /dev/cu.usbserial-1430 9600 -L
```

接入普通tc盒子，没有任何反应

接入ft2000机器，报错

