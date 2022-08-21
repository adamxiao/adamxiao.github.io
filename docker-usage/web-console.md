# web控制台

最终使用wetty验证效果不错, 就是还需要调整一些小细节
最终需求使用gotty实现实现不错, 就是输入法有点问题!

* wetty
  nodejs实现

* gotty

* https://github.com/rabchev/web-terminal
For fully featured TTY emulator I would suggest Wetty project.

* xterm.js

[容器 WebConsole 技术小结](https://joelei.com/2021/07/bcs-web-console-tech-summary/)
支持 VIM 等编辑操作
在 BCS WebConsole 的老版本中, 对 VI/VIM 支持是很差的, 使用会变现，无法保存等。

后面在看 rancher的实现, vscode的实现，发下他们对vim支持非常好, 和原生的命令行基本没有差别，在反复对比和测试后，发下主要是一个resize fit没有适配, 编码问题

[【干货】容器Web Console技术实现](https://cloud.tencent.com/developer/article/1416063)
基于GoTTY的Web Console开发

https://blog.csdn.net/liushuiwuyizhe/article/details/78263570
完成后将此功能单独开源，git地址是：https://github.com/lanbiter/docker-console  ,此项目owner就是本人
项目使用xterm.js + websocket + flask完成，按照项目下方步骤，很快就可以看见你的容器console了，如图所示：

https://github.com/WingkaiHo/docker-container-web-console
=> 这个源码非常简单, 做docker web console的


https://segmentfault.com/a/1190000022163850
web-console实现
无论是 docker exec还是 kubectl exec，都是接口操作，用起来比较麻烦。一般公司都会提供一个交互式的界面进行 exec 操作，称之为web-console，或者叫web-terminal、webshell

实现web-console的开源方案有很多，前端一般是xterm.js，主要难点在多租户隔离和权限校验。同时浏览器的以外关闭有可能导致 exec 残留，需要定时清理。

* web-console
* wssh
* KeyBox
* gotty
* GateOne
* dry
* toolbox
* xterm.js
* ttyd
以上方案中，最成熟的是gateone，其次是gotty

gateone：cka考试时使用的web shell就是基于gateone实现。含前端，python开发
gotty：完整的web shell实现，含前端，golang编写，方便二次开发

https://blog.51cto.com/u_15127630/2770869
唯品会Noah云平台实现内幕披露

#### GoTTY：把你的 Linux 终端放到浏览器里面

https://zhuanlan.zhihu.com/p/26590894

GoTTY 是一个简单的基于 Go 语言的命令行工具，它可以将你的终端（TTY）作为 web 程序共享。它会将命令行工具转换为 web 程序。

它使用 Chrome OS 的终端仿真器（hterm）来在 Web 浏览器上执行基于 JavaScript 的终端。重要的是，GoTTY 运行了一个 Web 套接字服务器，它基本上是将 TTY 的输出传输给客户端，并从客户端接收输入（即允许客户端的输入），并将其转发给 TTY。

它的架构（hterm + web socket 的想法）灵感来自 Wetty 项目，它使终端能够通过 HTTP 和 HTTPS 使用。

与docker一起使用
```
gotty -w -p 9000 -c "user:passwd" docker exec -it adam zsh
```

参数解析:
* 使用 -w 或 --permit-write 选项来允许客户端写入 TTY
* -p 9000配置端口(默认是8080端口)
* -c 配置基本用户名密码

=> very good

[GoTTY - 终端工具变为 Web 应用](https://blog.51cto.com/mageedu/2894786)
gotty的其他用法: k8s中使用gotty

#### wetty使用

参考github的使用方法:
```
docker run --rm -p 3000:3000 docker.io/wettyoss/wetty --ssh-host 10.20.1.99 --ssh-port 22345 --ssh-user adam
```

效果不错, 访问方式: http://10.20.1.99:3000/wetty

通过源码构建wetty镜像(由于有特殊权限要求，需要--privileged权限,所以使用buildx构建)
```
docker buildx build --allow security.insecure \
        --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
        --build-arg https_proxy=http://proxy.iefcu.cn:20172 \
        --platform=linux/arm64,linux/amd64 \
        -f containers/wetty/Dockerfile \
        -t hub.iefcu.cn/xiaoyun/wetty . --push
```

源码构建wetty多架构镜像: https://github.com/butlerx/wetty.git
```
commit 62fac799da92aa5d6e03c210ec248d643566a9bb (HEAD -> main, origin/main, origin/HEAD)
Author: Cian Butler <butlerx@notthe.cloud>
Date:   Wed Aug 17 19:16:33 2022 +0100

    Release 2.4.3
```

## 其他

关键字《web terminal》, 《容器web-console》

关键字《container-web-terminal》
[Setup Web Terminal using Wetty Docker Image](https://pacroy.medium.com/setup-web-terminal-using-wetty-docker-image-dcb1ea75bfaf)

这个验证可以, 但是屏幕太小
```
docker run \
    --name container-web-terminal \
    -p 9999:8888
    -v /var/run/docker.sock:/var/run/docker.sock \
    quay.io/enterprisecoding/container-web-term
```

最后使用连接进入
http://10.20.1.99:9999/?cid=adam&cmd=zsh

vscode终端很好用?
Hyper
https://zh.altapps.net/soft/iterm2?platform=linux
https://icode.best/i/89711634837507
https://www.jianshu.com/p/4b2b7074d9e2
https://blog.csdn.net/easylife206/article/details/103018688


## FAQ

#### 浏览器中的ctrl-w冲突使用

(macos没有这个问题。。。)
怎么办?

https://blog.miniasp.com/post/2020/09/29/Disable-Ctrl-W-keyboard-shortcut-in-Google-Chrome
安装插件, 禁用Ctrl+w, 改用Alt+w

安裝 Better Ctrl-W 擴充套件

開啟 Chrome 擴充功能的「鍵盤快速鍵」頁面

chrome://extensions/shortcuts
重新綁定快速鍵

請將 Ctrl-W 綁定到 Do absolutely nothing 即可停用 Chrome 預設 Ctrl-W 快速鍵！

再將 Alt-W 綁定到 Close highlighted tabs 即可用來取代原本關閉頁籤的快速鍵！

[如何修改Chrome浏览器快捷键？](https://www.zhihu.com/question/21333830)
=> 使用 Shortkeys 插件修改快捷键

[xterm.js - Shield the shortcut key of browser](https://github.com/xtermjs/xterm.js/issues/2812)
没办法屏蔽浏览器的快捷键啊

[(非常好)Disable hardwired chrome hot key ctrl+w?](https://superuser.com/questions/569248/disable-hardwired-chrome-hot-key-ctrlw)
https://github.com/thalesmello/better-ctrlw
=> 写一个插件, 映射ctrl-w这个事件！

http://www.kkh86.com/it/chrome-extension-doc/extensions/input.ime.html
=> google 插件api文档
chrome.input.ime.commitText

[Shortkeys - 自定义修改谷歌浏览器快捷键](https://www.fkxz.cn/logpjaacgmcbpdkdchjiaagddngobkck/?btwaf=31654479)
=> 使用shortkey定义快捷键, 运行js代码, 输入ctrl-w字符?

https://www.zhihu.com/question/21333830
推荐 Surfingkeys 插件，类Vimium插件，有上下翻页、用stack overflow搜索等等数不尽的快捷键，神器！

如果是单纯想禁用快捷键的话, Disable keyboard shortcuts.

[从零深入Chrome插件开发](https://xieyufei.com/2021/11/09/Chrome-Plugin.html)

[chrome快捷键太反人类?不想安装额外插件?那就用TamperMonkey写个脚本](https://toffee24.github.io/blog/2019/07/19/chrome%E5%BF%AB%E6%8D%B7%E9%94%AE%E5%A4%AA%E5%8F%8D%E4%BA%BA%E7%B1%BB-%E4%B8%8D%E6%83%B3%E5%AE%89%E8%A3%85%E9%A2%9D%E5%A4%96%E6%8F%92%E4%BB%B6-%E9%82%A3%E5%B0%B1%E7%94%A8TamperMonkey%E5%86%99%E4%B8%AA%E8%84%9A%E6%9C%AC/)
TamperMonkey

https://baiyunju.cc/8606
* 1：百度文库免费下载、内容自由复制、广告过滤等；
* 2：全网VIP视频免费破解(综合线路电视剧免跳出选集)支持爱奇艺、腾讯、优酷、哔哩哔哩等；
* 3：全网音乐、有声音频下载,支持网易云音乐、QQ音乐、酷狗、喜马拉雅、咪咕等；
* 4：知乎使用增强：外链接直接跳出、问题,回答时间标注、知乎短视频下载等；
* 5：短视频去水印下载(无限制下载)支持：抖音、快手；
* 6：CSDN使用增强：广告移除、净化剪切板、未登录查看折叠评论等；
* 7：京东、淘宝、天猫等优惠券查询……
