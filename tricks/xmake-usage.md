# xmake 编译使用

[Xmake v2.6.6 发布，分布式编译和缓存支持](https://zhuanlan.zhihu.com/p/519972771)

https://xmake.io/#/zh-cn/guide/project_examples

静态库程序
```
target("library")
    set_kind("static")
    add_files("src/library/*.c")

target("test")
    set_kind("binary")
    add_files("src/*c")
    add_deps("library")
```

```
mkdir xmake-build && cd xmake-build
xmake -F ../xmake.lua
```

指定只编译一个target
```
xmake -F ../xmake.lua xxx
```

arm架构处理, 甚至其他特殊架构!
=> arm理论上有，其他架构可以考虑使用源码编译出来吧! => run包本来就源码编译出来的，很快

生成sym文件
```
xmake -m debug # 不行，估计是旧版本的配置
xmake f -m debug
eu-strip xxx -f xxx.sym
```
=> 虽然debug编译了，但是没有定义debug的相关参数!

```
add_rules("mode.debug", "mode.release")

-- the release mode
if is_mode("release") then
	add_cxflags("-MD") 
-- the debug mode
elseif is_mode("debug") then
	add_cxflags("-MDd") 
end
```

关键字《xmake add specific file generation》

自定义目标, 前置操作
https://github.com/xmake-io/xmake/wiki/Xmake-v2.8.5-released,-Support-for-link-sorting-and-unit-testing#support-code-merging

https://github.com/xmake-io/xmake/issues/838
```
xxx
```

思路:
- 自定义rule
- on_build 调用其他target
- cmake的add_cust_command, cust target

https://xmake.io/mirror/manual/global_interfaces.html
引用子目录xmake配置
```
includes("subdirs")
includes("subdirs/xmake.lua")
includes("**/xmake.lua")
```

## 分布式编译配置

https://xmake.io/#/features/distcc_build?id=start-the-service

配置服务端
~/.xmake/service/server.conf
```
{
    known_hosts = { },
    logfile = "/root/.xmake/service/server/logs.txt",
    remote_build = {
        listen = "0.0.0.0:9691",
        workdir = "/root/.xmake/service/server/remote_build"
    },
    tokens = {
        "e438d816c95958667747c318f1532c0f"
    }
}
```

配置客户端
~/.xmake/service/client.conf
```
{
    distcc_build = {
        hosts = {
            {
                connect = "10.90.3.20:9691",
                njob = 8,
                token = "e438d816c95958667747c318f1532c0f"
            }
        }
    }
}
```

这个属于远程构建?
```
{
    remote_build = {
        connect = "127.0.0.1:9691",
        token = "e438d816c95958667747c318f1532c0f"
    }
}
```

客户端连接服务端
```
xmake service --connect # 远程编译连接?
xmake service --connect --distcc # 分布式编译连接
```

客户端开启分布式编译服务
```
xmake service --distcc
xmake service --distcc -vD
```

## 其他

常用
```
xmake    编译
xmake f -c   清缓存
xmake clean  
xmake project -k vsxmake -m "debug,release"   生成vs工程
xmake -j2
xmake f --ccache=n --cxx="ccache gcc" --cc="ccache gcc"
```

https://xmake.io/mirror/guide/configuration.html
```
xmake f --help # 配置
```

链接库排序, 2.8.5的新功能
```
add_links("a", "b", "c", "d", "e")
-- e -> b -> a
add_linkorders("e", "b", "a")
--e->d
add_linkorders("e", "d")
```

https://xmake.io/mirror/plugin/builtin_plugins.html
Generate CMakelists.txt
=> 生成CMakefile?

- [xmake新增智能代码扫描编译模式](https://www.cnblogs.com/tboox/p/12014652.html)

https://xmake.io/mirror/manual/builtin_variables.html
使用shell命令生成变量
```
add_defines("$(shell uname -m)") -- 根据当前架构生成 -Daarch64
```

## FAQ

#### error: assertion failed!

=> 语法代码执行错误了，修正即可

https://github.com/xmake-io/xmake/issues/36
加-v --backtrace 参数编译看下

## 参考资料

- [构建语法参考](https://xmake.io/#/manual/project_target?id=targetadd_defines)

- [使用 xmake 为游戏引擎构建灵活与高并发的构建系统](https://zhuanlan.zhihu.com/p/571396425)

- [Xmake Getting Started Tutorial 4: C/C++ project description settings](https://tboox.org/2019/11/10/quickstart-4-basic-project-settings/)
  => 入门，挺好的

- [内置模块](https://xmake.io/mirror/zh-cn/manual/builtin_modules.html)
  os.runv

- [xmake 源码架构剖析](https://juejin.cn/post/6844903501244399629)
