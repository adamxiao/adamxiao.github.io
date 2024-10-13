# gdb使用

#### 查看修改寄存器的值

关键字`gdb 修改寄存器的值`
https://chyyuu.gitbooks.io/ucore_os_docs/content/lab0/lab0_2_3_3_gdb.html

关键字`gdb print eax`
https://stackoverflow.com/questions/5429137/how-to-print-register-values-in-gdb
```
info registers eax
```

查看寄存器的值
```
info registers
i r
info all-registers
info registers eax
```

修改寄存器的值
```
set $eax = 0    ---- 通过set命令修改eax的值，与变量不同，修改寄存器的值时，需要在寄存器名称前加'$'
```

#### 寄存器分类

分析这几个寄存器是什么意思?
eax, rbp ?
```
   0x5555555551af <verify_password+38>: mov    %eax,-0x4(%rbp)
   0x5555555551b2 <verify_password+41>: mov    -0x4(%rbp),%eax
   0x5555555551b5 <verify_password+44>: leave
   0x5555555551b6 <verify_password+45>: ret
```

EAX 是"累加器"(accumulator), 它是很多加法乘法指令的缺省寄存器。

https://blog.csdn.net/zhu2695/article/details/16813425
Eax用来保存所有API函数的返回值。 => 好像是的额

https://blog.csdn.net/weixin_45844670/article/details/110495341
EAX - Accumulator Register（累加器）
当你写一个函数，最后返回一个值x（return x），那么这个x就要被存到%eax.
当你要把一个数字扩展成64位，那么%eax存这个数的低32位，%edx存这个数的高32位。

#### 显示汇编指令

关键字`gdb 显示汇编`

用gdb 查看汇编代码， 采用disassemble 和 x 命令。 nexti, stepi 可以单步指令执行

https://blog.csdn.net/counsellor/article/details/100034080
查看当前执行及后20行汇编指令
```
display /20i $pc
```


#### 其他

查看堆栈
```
bt full
thread apply all bt full
```

#### 调试qemu程序

```
handle  SIGUSR2  nostop  noprint  pass
handle  SIGIO    nostop  noprint  pass
handle  SIGALRM  nostop  noprint  pass
handle  SIGPIPE  nostop  noprint  pass
handle  SIGSEGV  stop    print
cont
bt full
thread apply all bt full
finish
quit
```

#### 调试子进程

```
set follow-fork-mode child
```
