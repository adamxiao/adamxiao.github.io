# python编写脚本

#### 破解linux shadow密码

[/etc/shadow可以获取原密码吗](https://www.jianshu.com/p/b18f545fe451)

```
import crypt   ## 导入 Linux 口令加密库
def testPass(cryptPass):
    salt=cryptPass[cryptPass.find("$"):cryptPass.rfind("$")]  ## 获得盐值，包含 $id 部分
    dictFile=open('key.txt','r')
    for word in dictFile.readlines():
        word=word.strip("\n")
        cryptWord=crypt.crypt(word,salt)                   ## 将密码字典中的值和盐值一起加密
        if (cryptWord==cryptPass):                           ## 判断加密后的数据和密码字段是否相等
            print ("[+]Found Password:"+word+"\n" )      ## 如果相等则打印出来
            return 
    print ("[-] Password Not Found.\n")
    return 
 
def main():
    passFile=open('shadow.txt')
    for line in passFile.readlines():      ## 读取文件中的所有内容
        if ":" in line:
            user=line.split(":")[0]                     ## 获得用户名
            cryptPass=line.split(":")[1].strip(' ')     ## 获得密码字段
            print ("[*] Cracking Password for:"+user)
            testPass(cryptPass)
main()
```

或者使用john命令破解
```
apt install -y john # 安装工具
unshadow fusion-passwd fusion-shadow > 1.txt # 准备工作
john 1.txt --format=crypt # 使用默认字典破解

john --wordlist=key.txt 1.txt --format=crypt # 使用自定义字典破解
john --show 1.txt # 展示破解的密码
```

#### 调试python脚本

调试python脚本的方法, 类似gdb的单步调试命令
```
import pdb
pdb.set_trace() # 在想要断点的地方加一行命令
```

#### logging使用

```
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

exception = logger.exception
error = logger.error
info = logger.info
warning = logger.warning
debug = logger.debug

logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.setLevel(logging.WARNING)
logger.setLevel(logging.ERROR)
logger.setLevel(logging.FATAL)
```


#### python tcp socket server

https://realpython.com/python-sockets/#echo-server

```
# echo-server.py

import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
```

https://docs.python.org/3/library/socketserver.html
python3 标准模块 socketserver

#### 递归扫描文件

关键字《python scan files recursively》

https://www.tutorialspoint.com/How-to-scan-through-a-directory-recursively-in-Python
https://stackoverflow.com/questions/2186525/how-to-use-to-find-files-recursively
- Using os.walk() method
- Using glob.glob() method
- Using os.listdir() method

使用glob正则匹配?
(注意: recursive参数需要python3.5以上支持)
```
from glob import glob

for filename in glob('src/**/*.c', recursive=True):
    print(filename)   
```

使用os.walk
```
import fnmatch
import os

matches = []
for root, dirnames, filenames in os.walk('src'):
    for filename in fnmatch.filter(filenames, '*.c'):
        matches.append(os.path.join(root, filename))
```

非递归, 只遍历文件
```
from os import listdir
from os.path import isfile, join
 
directory_path = 'D:\\mydir'
files = [f for f in listdir(directory_path) if isfile(join(directory_path, f))]
print(files)
```

#### thread lock使用共享数据

https://www.pythonforthelab.com/blog/handling-and-sharing-data-between-threads/

```
from threading import Lock
[...]
data_lock = Lock()
def modify_variable(var):
    while True:
        for i in range(len(var)):
            with data_lock:
                var[i] += 1
        if event.is_set():
            break
        # sleep(.5)
    print('Stop printing')
```

#### thread异步调用外部程序

https://juejin.cn/s/python%20异步执行shell命令

```
import subprocess
import threading

def run_command(command):
    subprocess.call(command, shell=True)

command = "ls -l"
thread = threading.Thread(target=run_command, args=(command,))
thread.start()
```

#### subprocess 调用外部程序

```
import subprocess

try:
	subprocess.check_call(['ipmitool', 'sel', 'time', 'set', t])
	return 0
except subprocess.CalledProcessError as error:
	info('failed to set sel time')
	return -1
```

#### try except

https://www.w3schools.com/python/python_try_except.asp

```
try:
  f = open("demofile.txt")
  try:
    f.write("Lorum Ipsum")
  except:
    print("Something went wrong when writing to the file")
  finally:
    f.close()
except:
  print("Something went wrong when opening the file")

x = -1
if x < 0:
  raise Exception("Sorry, no numbers below zero")
```

https://docs.python.org/3/tutorial/errors.html

```
try:
    res = 190 / 0
except Exception as error:
    # handle the exception
    print("An exception occurred:", error) # An exception occurred: division by zero
```

#### escape shell command

How to escape os.system() calls?

https://stackoverflow.com/questions/35817/how-to-escape-os-system-calls

shlex.quote() does what you want since python 3.

```
def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"
```

https://www.geeksforgeeks.org/how-to-replace-values-in-a-list-in-python/
```
sys.argv = list(map(lambda x: shellquote(x), sys.argv))
```

#### execve, setuid

切用户执行进程, 看能不能su处理?
```
import pwd
pw = pwd.getpwnam("kylin-ksvd")
uid = pw.pw_uid
os.setuid(uid)
sys.argv[0] = "/usr/lib/ksvd/bin/ksvd-mc-runas"
arguments = sys.argv[1:]
os.execlp(sys.argv[0], sys.argv[0], *arguments) # https://lisper.in/fork-exec-python
```

#### strip

- trim()可以去除字符串前后的**半角空白字符**
- strip()可以去除字符串前后的**全角和半角空白字符**
