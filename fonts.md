# fonts usage

## 零碎知识收集
- vim只能用终端的字体,gvim能自定义字体
- ubuntu的字体配置在/usr/share/fonts目录下
- ubuntu的gnome-terminal配置的字体为Ubuntu Mono Regular 13, 这个字体我发现`复`这个字展示有问题
后来不知道怎么就修复成功了，默认没有这个问题
- 通过Character Map(`gucharmap`)这个软件查看ubuntu上安装的所有的字体的效果
- 实时改变gnome-terminal的字体配置，也能实时看字体效果

## FAQ

#### ubuntu 24.04 wps字体粗体问题

安装宋体后解决

关键字《ubuntu simsun font downloads》

[ubuntu 黑体 Ubuntu 字体安装](https://blog.csdn.net/weixin_39620578/article/details/111753414)
1.建立一个新的fonts目录来存放需要的字体。
```
sudo mkdir /usr/share/fonts/zh_CN
```
2.可以从安装了windows的机器上拷贝如下的字体到上面建立的目录内。
注：windows的字体一般存放在c:\windows\fonts目录下，以上字体凭自己爱好挑选，参考
- simhei.ttf 黑体

[Ubuntu 下载常用字体](https://pipboy.cn/code/server/linux/ubuntuFont.html)
```
sudo apt update
sudo apt install ttf-mscorefonts-installer
```
这个软件包包含了一些常用的微软字体，如宋体、微软雅黑等，并且支持中文字符。
=> 但是没有黑体

[Google Fonts](https://fonts.google.com/specimen/Ubuntu?preview.text=simhei)
=> 参考neovim安装Nerd字体, 下载下将ttf文件解压到指定目录
