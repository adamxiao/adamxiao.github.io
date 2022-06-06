# web控制台

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
docker run --rm -p 3000:3000 wettyoss/wetty --ssh-host 10.20.1.99 --ssh-port 22345 --ssh-user adam
```

效果不错

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

