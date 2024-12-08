# ccache使用

[ccache的GitLab配置项中没有命中](https://cloud.tencent.com/developer/ask/sof/199912)
问题出在ccache检查编译器是否相同的默认方式--通过它的时间戳。由于每个Docker CI实例都运行一个全新的GitLab容器，因此此时间戳总是不同的，因此总是构建新的缓存。
要解决此问题，请将CCACHE_COMPILERCHECK设置为content，而不是默认的mtime

[ccache使用简介](https://blog.csdn.net/LeMark2333/article/details/127839318)
https://juejin.cn/post/7165510954850418719

ccache的使用方式
- ccache 拉起编译命令
  ccache g++ -c hello.cpp -o hello.o
- ccache伪装成编译器
  ln -s /usr/bin/ccache g++
  g++ -c hello.cpp -o hello.o

ccache提供了查询缓存命中能力
执行 ccache -s -v

https://github.com/xmake-io/xmake/issues/2425
xmake关于ccache的问题讨论

https://xuanwo.io/reports/2023-04/
Sccache 共享缓存
