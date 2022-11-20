# elf反汇编破解

关键字`二进制程序 反编译 破解`

思路:
- 实时gdb调代码, 修改值
  临时修改一次而已, 需要永久修改
- 根据上一步, gdb反汇编得到具体的汇编指令，然后修改掉?
- gdb展示汇编代码?

问题:
- objdump反汇编之后,怎么修改,然后编译回去?

https://cn-sec.com/archives/490192.html
本系列为二进制破解科普系列教程。教程面向新手爱好者
讲了汇编的一些基础知识

https://www.v2ex.com/t/696622
golang 二进制程序，容易被破解吗？
反汇编的一些讨论...
有简单的反汇编破解

#### 先来一个入门破解示例

初识二进制与软件破解
https://blog.csdn.net/sdihvai/article/details/105268580
=> 还行吧，是windows下的示例

实验的思路来自《0day安全：软件漏洞技术分析》第一章。此次实验的内容为如何破解一个简单的密码验证功能的exe文件。通过此次实验可以大体了解软件破解的一些步骤，为二进制漏洞的学习打下基础认知。

1.首先编写一个简单的密码验证的可执行文件。语言为C++（其他语言也可以，只要能生成exe）。
```cpp
#include <stdio.h>
#include <string.h>

#define PASSWORD "123456"

int verify_password(char *p){
    int flag;
    flag = strcmp(p,PASSWORD);
    /*return flag;*/
    return 123;
}

int main(){
    char password[10];
    while(1){
        printf("input your password:\n");
        scanf("%s",password);
        if (verify_password(password)==0){
            printf("TRUE\n");
        }else{
            printf("FALSE\n");
        }
    }
    return 0;
}
```

当输入123456时返回TRUE表示密码正确，其他字符返回FALSE
(我改动了一点点，方便简单修改, 永远返回错误码123)

2.编译生成二进制，然后使用objdump反编译等
```
gcc pwn.c -o pwn
objdump -s -d pwn > pwn.txt
xxd pwn > pwn.xxd
```

3.修改里面汇编指令，返回true
```
    11b2:       b8 7b 00 00 00          mov    $0x7b,%eax
修改为如下(简单修改二进制文本文件pwn.xxd)=>
    11b2:       b8 00 00 00 00          mov    $0x0,%eax
```

0.修改调用函数，改为把函数的返回码直接改为0
(可以让二进制程序检查接口跳过，永远返回真。)
```
$ diff qemu.xxd /mnt/qemu.xxd
  1ad787:       e8 3b 0f 3c 00          call   56e6c7 <xxx_check_func>
改为
  1ad787:       b8 00 00 00 00          mov    $0x0,%eax
```

#### 如何反汇编

关键字`linux 反汇编工具`

https://blog.csdn.net/weixin_30350163/article/details/116774960
Linux 反汇编工具,逆向与反汇编工具
=> 粗略介绍一些简单的工具

记得以前用过 objdump 这个工具

好像记得 readelf 这个工具还能够获取到一些什么信息?

还有以前用到 addr2line 干嘛用的?


https://zhuanlan.zhihu.com/p/335550245
objdump(Linux)反汇编命令使用指南
=> 只讲了objdump简单的反汇编, 怎么修改,之后再汇编回去呢?


https://www.jianshu.com/p/491bd2346277
在linux上开IDA会比较麻烦，相比较之下，可以用objdump就来反汇编二进制文件，想用就用，而且可以指定反汇编的节，使得反汇编工作更轻量。
```
objdump -D obj  ##查看所有节段反汇编代码
objdump -d obj   ##查看所有可执行节的反汇编代码
objdump -j .text -S obj   ##查看elf文件指定节的反汇编代码
```

[反汇编和二进制分析工具清单 原创](https://blog.51cto.com/u_13127751/5209594)
本文摘自《二进制分析实战》
=> 提了很多真正专业的工具(好工具要收费的)


Linux下的二进制工具(反编译工具)
http://blog.cuicc.com/blog/2011/07/20/binutils-of-linux/
关键字


The GNU Binutils are a collection of binary tools. The main ones are:

- ld - the GNU linker.
- as - the GNU assembler.

But they also include:

- addr2line - Converts addresses into filenames and line numbers.
- ar - A utility for creating, modifying and extracting from archives.
- c++filt - Filter to demangle encoded C++ symbols.
- dlltool - Creates files for building and using DLLs.
- gold - A new, faster, ELF only linker, still in beta test.
- gprof - Displays profiling information.
- nlmconv - Converts object code into an NLM.
- nm - Lists symbols from object files.
- objcopy - Copys and translates object files.
- objdump - Displays information from object files.
- ranlib - Generates an index to the contents of an archive.
- readelf - Displays information from any ELF format object file.
- size - Lists the section sizes of an object or archive file.
- strings - Lists printable strings from files.
- strip - Discards symbols.
- windmc - A Windows compatible message compiler.
- windres - A compiler for Windows resource files.

Most of these programs use BFD, the Binary File Descriptor library, to do low-level manipulation. Many of them also use the opcodes library to assemble and disassemble machine instructions.

The binutils have been ported to most major Unix variants as well as Wintel systems, and their main reason for existence is to give the GNU system (and GNU/Linux) the facility to compile and link programs.

The detail introduction and use guide is documentation for binutils 2.21.

在Linux下，可执行文件即是目标文件，一般情况下可通过以下三个命令查看反汇编信息：

nm命令列出目标文件的所有符号，如：

$nm a.out | more
objdump命令列出目标文件的详细汇编信息

$objdump -S a.out | more 
readelf 是列出文件的ELF格式的内容

$readelf --debug-dump a.out | more 
关于这三个命令的详细参数，以及其他命令的使用可以参看上面的文档binutils 2.21。反汇编文件这里没有列出，主要是个人觉得分析起来有点难。反汇编的信息对于了解程序的架构很有帮助，但是很难得到具体的程序信息，我本想查看程序返回值，看了半天没有结论。。。

#### objdump反汇编

```
源码编译为汇编代码
gcc -S -o main.s main.c

目标文件反汇编
gcc -c -o main.o main.c
objdump -s -d main.o > main.o.txt

1.3 可执行文件反汇编
gcc -o main main.c
objdump -s -d main > main.txt
```


#### crackmes验证?

https://developer.aliyun.com/article/534785
正如C语言教程从 hello world 开始，我们也由一个 crackme 说开去。本文的例子程序你可以到这来下载:
http://www.crackmes.de/users/veneta/crackmes/linux_crackme_v2 。

#### 试用ida-free

https://hex-rays.com/ida-free/

=> 装好了,但是不会用

#### Reko源码和工具的下载

https://blog.csdn.net/u011426115/article/details/112077441

逆向工程师...
利用Ghidra逆向分析Go二进制程序（上篇）
https://www.4hou.com/posts/8OJ2
