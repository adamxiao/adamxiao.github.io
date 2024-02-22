# cmake使用

## 优点:
1. 编译只需敲make
2. cmake自动解决头文件依赖问题, 再也不需要重新编译各种comm库
3. 生成文件和svn源文件完全隔离
4. cmakefile简洁抽象易懂

## 使用cmake
1. 创建CMakeLists.txt
2. 定义include_path, complie_flags, link_library
3. 定义protobuf和jce目标规则(参考cmake的标准模块FindProtobuf)
4. 定义server，daemon, tools编译目标
5. 使用单独build目录生成所有动态库，可执行文件

## 常用cmake语法
1. `INCLUDE_DIRECTORIES`全局include路径
2. `LINK_LIBRARIES`全局link库
3. `FILE(GLOB svr_src "*.cpp")`正则文件列表定义
4. `ADD_LIBRARY`定义静态动态库目标
5. `ADD_EXECUTABLE`定义可执行目标
6. `ADD_CUSTOM_TARGET`自定义目标
7. `ADD_CUSTOM_COMMAND`自定义依赖文件生成规则
8. `ADD_SUBDIRECTORY`包含子目录cmake文件

## 小技巧
1. 使用`EXCLUDE_FROM_ALL`标识，默认不编译目标
2. 使用`export MAKEFLAGS='-j4'`默认开启并行编译
3. 使用`make VERBOSE=1`查看编译命令细节

## 入门使用

```
# CMake 最低版本号要求
cmake_minimum_required (VERSION 2.8)

# 项目信息
project (Demo1)

# 指定生成目标
add_executable(Demo main.cc)
```

https://www.hahack.com/codes/cmake/

指定多个源文件
```
# 查找当前目录下的所有源文件
# 并将名称保存到 DIR_SRCS 变量
aux_source_directory(. DIR_SRCS)
```

或者手动指定源文件
```
set(SOURCE_FILES
    main.cpp
    utils.cpp
    )
```

```
include_directories ("${PROJECT_SOURCE_DIR}/math")
```

设置目标编译宏
```
target_compile_definitions(your_target PRIVATE DEBUG=1)
```

https://stackoverflow.com/questions/7990844/creating-symbol-table-for-gdb-using-cmake
生成sym文件?
set(CMAKE_BUILD_TYPE Debug)

https://gitlab.kitware.com/cmake/community/-/wikis/FAQ#how-can-i-generate-a-source-file-during-the-build
生成中间源文件?

## 参考资料
1. https://samthursfield.wordpress.com/2015/11/21/cmake-dependencies-between-targets-and-files-and-custom-commands/
