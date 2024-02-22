# 分布式编译distcc使用

关键字《ccache 分布式编译》

https://blog.csdn.net/zhgeliang/article/details/78709821

- 1.使用tmpfs来代替部分IO读写
- 2.ccache，可以将ccache的缓存文件设置在tmpfs上，但是这样的话，每次开机后，ccache的缓存文件会丢失
- 3.distcc,多机器编译
- 4.将屏幕输出打印到内存文件或者/dev/null中，避免终端设备（慢速设备）拖慢速度。

使用distcc，并不像想象中那样要求每台电脑都具有完全一致的环境，它只要求源代码可以用make -j并行编译，并且参与分布式编译的电脑系统中具有相同的编译器。

[分布式编译发展历程](https://juejin.cn/post/7283710975345115199)

除了distcc本身在不断进化，开源界也孵化了另一个基于distcc的解决方案icecream，它的工作原理和distcc类似，但在任务调度方面做了更多的优化。distcc 需要使用者手动配置server列表，而icecream使用了更高级的分布式调度器和负载均衡器来优化任务分发和节点管理。

鉴于ccache在跨机器复用能力的不足，Mozilla（rust语言的母公司）在ccache的基础上开发了集群版的sccache， 它不仅可以使用本地磁盘存储编译产物，也可以将编译产物发送到云端，并对接AWS S3，Azure，Google Cloud Stroage等对象存储服务。

[Xmake v2.6.6 发布，分布式编译和缓存支持](https://zhuanlan.zhihu.com/p/519972771)

使用了 Xmake，就等于同时使用了 distcc/ccache/sccache。

[开源公告｜C++分布式编译系统yadcc开源了](https://cloud.tencent.com/developer/article/1832308)
=> 前提: 使用make -j

[美团 - C++服务编译耗时优化原理及实践](https://tech.meituan.com/2020/12/10/apache-kylin-practice-in-meituan.html)

## xmake使用

分布式编译缺点: 预编译，链接还是在本地!

## 预编译分布式?

[让工程师拥有一台“超级”计算机——字节跳动客户端编译加速方案](https://juejin.cn/post/7065533288995094541)
Google的 goma 采用了自研的依赖分析模块，并且在Chromium和Android这两个大型项目上取得了非常好的结果。它在实现依赖分析的时候，借助常驻进程的架构优势，运用了大量缓存，索引等技巧，提高了中间数据的复用率。

[分布式编译发展历程](https://juejin.cn/post/7283710975345115199)
goma选择了一条复杂的道路，它自研了一套依赖分析引擎，通过读文件的方式，直接分析代码中的 #include预处理指令，实现了更快速的依赖分析能力。为了提高对操作系统的复用度，goma还把依赖分析做成了常驻进程compiler_proxy，性能得到了极大的提升，使用goma甚至可以达到**几百的编译并行度**。

面向分布式存储系统结构的 OpenMP 编译系统
https://dds.sciengine.com/cfs/files/pdfs/view/1674-7267/RbWxnZMjoRv85e8S2.pdf

华为云发布分布式编译构建系统 CodeArts Build
https://my.oschina.net/u/4526289/blog/7820582

https://www.incredibuild.cn/
加速开发周期和上市时间，以更低的成本，
获得更多的本地和云上计算能力。
