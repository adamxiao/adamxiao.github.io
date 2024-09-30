# openwrt使用

关键字《openwrt opkg 更新使用代理》

https://mirrors4.tuna.tsinghua.edu.cn/help/openwrt/
=> 使用国内源
```
sed -i 's_https\?://downloads.openwrt.org_https://mirrors.tuna.tsinghua.edu.cn/openwrt_' /etc/opkg/distfeeds.conf
```
