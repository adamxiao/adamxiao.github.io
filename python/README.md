# python编写脚本

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
