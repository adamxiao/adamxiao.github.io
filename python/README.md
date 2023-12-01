# python编写脚本

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
