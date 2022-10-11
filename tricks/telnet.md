# telnet使用

## 搭建telnet服务

关键字`socat  telnet server`

http://tiebing.blogspot.com/2011/08/simple-telnet-server-by-using-socat.html

这个直接通过telnet暴露出了tty
```
#On server side:
socat exec:'bash -li',pty,stderr,setsid  tcp-listen:8999,reuseaddr

#On client side:
socat tcp-connect:127.0.0.1:8999 file:`tty`,raw,echo=0
```

socat tcp-listen:12345,reuseaddr tcp-listen:8999,reuseaddr


#### 使用nc搭建

关键字`nc telnet server`

```
nc -k -l 8999
```

客户端使用
```
nc -w3 -4 -v www.redhat.com 80
```

参数解析
* -w3表示３秒超时
* -4 means to use IPV4
