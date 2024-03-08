# python2转python3

## 旧的资料

单号 2036

直接运行2to3.py脚本
```
#!/usr/bin/python
import sys
from lib2to3.main import main

sys.exit(main("lib2to3.fixes"))
```

```
./2to3.py -w /xxx/xxx/a.py 
```

python2 到 python3的方法
流程

    1 修改语法：通过2to3.py脚本，解决大部分python脚本的语法问题 具体命令，如修改a.py：/home/work/2to3.py -w /xxx/xxx/a.py 

    2 调试：运行脚本，进行微调

    3 功能测试

 

2to3.py常见问题：

    /home/work/2to3.py -w /xxx/xxx/a.py  

   -w 修改文件，不加-w， 显示修改后的效果。

   经验1：不要重复运行命令

   经验2：保存修改前的文件，方便比对
python2 python3的区别

        参考： https://www.runoob.com/python/python-2x-3x.html 
        1 print xx 变为 print (xx)
        2 Unicode Python 2 有 ASCII str() 类型，unicode() 是单独的，不是 byte 类型; 在 Python 3，我们最终有了 Unicode (utf-8) 字符串，以及一个字节类：byte 和 bytearrays。
        3 除法运算: 整数相除的结果是一个整数，把小数部分完全忽略掉，浮点数除法会保留小数点的部分得到一个浮点数的结果; python3 保留浮点数。
        4 异常： 捕获异常的语法由 except exc, var 改为 except exc as var。
        5 xrange不存在了： range() 是像 xrange() 那样实现以至于一个专门的 xrange() 函数都不再存在（在 Python 3 中 xrange() 会抛出命名异常）
        6 八进制数：必须写成0o777，原来的形式0777不能用了；二进制必须写成0b111
        7 Python 3.x中去掉了<>不等于符号
        8 Python 3.x 中去掉了``这种写法，只允许使用repr函函数，expr将对象装换为字符创
        9 包被改名：_winreg    winreg/ConfigParser    configparser/copy_reg    copyreg/Queue    queue/SocketServer    socketserver/repr    reprlib
          io StringIO模块现在被合并到新的io模组内。 new, md5, gopherlib等模块被删除。 Python 2.6已经支援新的io模组。
          http httplib, BaseHTTPServer, CGIHTTPServer, SimpleHTTPServer, Cookie, cookielib被合并到http包内。
          exec 取消了exec语句，只剩下exec()函数。 Python 2.6已经支援exec()函数。
        10 Py3.X用int替换long类型
        11 新增了bytes类型： str 对象和 bytes 对象可以使用 .encode() (str -> bytes) 或 .decode() (bytes -> str)方法相互转化。
        12 dict的.keys()、.items 和.values()方法返回迭代器，而之前的iterkeys()等函数都被废弃。同时去掉的还有 dict.has_key()，用 in替代它吧 
 
常见错误

            问题1：tab和空格 对齐的问题
                [root@node1 bin]# ./ksvd-vde-menu --help
                Traceback (most recent call last):
                  File "/usr/lib/ksvd/bin/./ksvd-vde-menu", line 29, in <module>
                    import KsvdNetConfig
                  File "/usr/lib/ksvd/etc/python/KsvdNetConfig.py", line 453
                    ipaddr = ipaddr_info.read().strip().replace(';', '')
                TabError: inconsistent use of tabs and spaces in indentation
                [root@node1 bin]#
            A：在vim set noexpandtab，不自动转为空格。
            
            问题2：sys没有setdefaultencoding方法的问题
                Traceback (most recent call last):
                    File "/usr/lib/ksvd/bin/./rc.ksvd-ovs-network", line 43, in <module>
                    sys.setdefaultencoding('utf8')
                AttributeError: module 'sys' has no attribute 'setdefaultencoding'
            A：不使用就可以了。

 

            问题3：0x90无法转换？
                [root@node3 bin]# /home/work/2to3.py -n -w /usr/bin/heketi* 
                RefactoringTool: Skipping optional fixer: buffer
                RefactoringTool: Skipping optional fixer: idioms
                RefactoringTool: Skipping optional fixer: set_literal
                RefactoringTool: Skipping optional fixer: ws_comma
                Traceback (most recent call last):
                  File "/home/work/2to3.py", line 5, in <module>
                    sys.exit(main("lib2to3.fixes"))
                  File "/usr/lib64/python3.9/lib2to3/main.py", line 263, in main
                    rt.refactor(args, options.write, options.doctests_only,
                  File "/usr/lib64/python3.9/lib2to3/refactor.py", line 690, in refactor
                    return super(MultiprocessRefactoringTool, self).refactor(
                  File "/usr/lib64/python3.9/lib2to3/refactor.py", line 286, in refactor
                    self.refactor_file(dir_or_file, write, doctests_only)
                  File "/usr/lib64/python3.9/lib2to3/refactor.py", line 731, in refactor_file
                    return super(MultiprocessRefactoringTool, self).refactor_file(
                  File "/usr/lib64/python3.9/lib2to3/refactor.py", line 326, in refactor_file
                    input, encoding = self._read_python_source(filename)
                  File "/usr/lib64/python3.9/lib2to3/refactor.py", line 322, in _read_python_source
                    return f.read(), encoding
                  File "/usr/lib64/python3.9/codecs.py", line 322, in decode
                    (result, consumed) = self._buffer_decode(data, self.errors, final)
                UnicodeDecodeError: 'utf-8' codec can't decode byte 0x90 in position 24: invalid start byte
                [root@node3 bin]# 
            A：存在2进制程序。

 

            问题4：TypeError: a bytes-like object is required, not 'str'
             ./heketi_check_disk_status.py 
                Traceback (most recent call last):
                  File "/usr/bin/./heketi_check_disk_status.py", line 189, in <module>
                    sys.exit(main())
                  File "/usr/bin/./heketi_check_disk_status.py", line 182, in main
                    disk_list = get_disk_list()
                  File "/usr/bin/./heketi_check_disk_status.py", line 40, in get_disk_list
                    items = line.split('"')
                TypeError: a bytes-like object is required, not 'str'
            A：
                解决思路
                问题出在python3.5和Python2.7在套接字返回值解码上有区别:
                python bytes和str两种类型可以通过函数encode()和decode()相互转换，
                str→bytes：encode()方法。str通过encode()方法可以转换为bytes。
                bytes→str：decode()方法。如果我们从网络或磁盘上读取了字节流，那么读到的数据就是bytes。要把bytes变为str，就需要用decode()方法。


                解决方法
                将line.strip().split(",")  改为  line.decode().strip().split(",")

                原文链接：https://blog.csdn.net/qq_41185868/article/details/83833262

 

            问题5：TypeError: cannot use a string pattern on a bytes-like object
                [root@node3 bin]# ./heketi_check_disk_status.py 
                Traceback (most recent call last):
                  File "/usr/bin/./heketi_check_disk_status.py", line 189, in <module>
                    sys.exit(main())
                  File "/usr/bin/./heketi_check_disk_status.py", line 185, in main
                    total_disk_status(disk_list)
                  File "/usr/bin/./heketi_check_disk_status.py", line 165, in total_disk_status
                    disk_info = smartctl_disk(disk_name)
                  File "/usr/bin/./heketi_check_disk_status.py", line 130, in smartctl_disk
                    match = re.match(pattern_overall_health, line)
                  File "/usr/lib64/python3.9/re.py", line 191, in match
                    return _compile(pattern, flags).match(string)
                TypeError: cannot use a string pattern on a bytes-like object
                [root@node3 bin]# 
            A：    line = a_line.decode()

 

            问题6：ValueError: could not convert string to float: ''
                [root@node3 bin]# ./heketi_disk_detect.py "/dev/sdc"
                Traceback (most recent call last):
                  File "/usr/bin/./heketi_disk_detect.py", line 198, in <module>
                    sys.exit(main())
                  File "/usr/bin/./heketi_disk_detect.py", line 188, in main
                    if check_load_average(sys.argv[idx + 1]) == False:
                  File "/usr/bin/./heketi_disk_detect.py", line 156, in check_load_average
                    disk_util = get_disk_util(dev_name)
                  File "/usr/bin/./heketi_disk_detect.py", line 148, in get_disk_util
                    return float(disk_util)
                ValueError: could not convert string to float: ''
                [root@node3 bin]# 
            A：float()

 

            问题7：module 'string' has no attribute 'atoi'？  atof
                [root@node3 bin]# ./heketi_volume_disk_info.py --help
                Traceback (most recent call last):
                  File "/usr/bin/./heketi_volume_disk_info.py", line 429, in <module>
                    sys.exit(main())
                  File "/usr/bin/./heketi_volume_disk_info.py", line 425, in main
                    merge_data()
                  File "/usr/bin/./heketi_volume_disk_info.py", line 78, in merge_data
                    size = string.atoi(devsize)
                AttributeError: module 'string' has no attribute 'atoi'
                [root@node3 bin]#
            A：
                python2 中可以用string.atoi 在python3中会报错，替换的方案是
                string.atoi(your_str)
                1
                替换为
                int(your_str)
                1
                这个代码python2和python3都可以运行，如果是atof，就改为float。
                
            问题8：TypeError: a bytes-like object is required, not 'str'
                > /usr/lib/ksvd/etc/python/KsvdUtil.py(663)SysCall2()
                -> return output.rstrip('\n')
                (Pdb) n
                TypeError: a bytes-like object is required, not 'str'
                > /usr/lib/ksvd/etc/python/KsvdUtil.py(663)SysCall2()
                -> return output.rstrip('\n')
            A: output.decode()
                
            问题9：NameError: name 'cmp' is not defined
                Traceback (most recent call last):
                  File "/usr/lib/ksvd/etc/python/KsvdApp.py", line 171, in AppSequence
                    rc = self.InvokeApp()
                  File "/usr/lib/ksvd/bin/rc.ksvd-ovs-network", line 439, in InvokeApp
                    milestone = StartNetworking(True, doStart)
                  File "/usr/lib/ksvd/bin/rc.ksvd-ovs-network", line 307, in StartNetworking
                    if cmp(dataMountPointListOfConf, currDataMountPoint):
                NameError: name 'cmp' is not defined
            A：cmp 改为 ==
