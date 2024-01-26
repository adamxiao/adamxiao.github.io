# nps代理使用

## 探索

关键字《linux nps是什么》

https://ehang-io.github.io/nps/#/

配置文件
https://github.com/ehang-io/nps/tree/master/conf
- 访问服务端ip:web服务端口（默认为8080）
- 使用用户名和密码登陆（默认admin/123，正式使用一定要更改）
- 创建客户端

docker容器启用nps
```
docker run -d --name nps --net=host -v $PWD/conf:/conf ffdfgdfg/nps
```

首先在nps管理界面添加一个客户端, 然后客户端就可以连接了
```
./npc -server=x.x.x.x:8024 -vkey=xxx -type=tcp
docker run 
无配置文件
docker run -d --name npc --net=host ffdfgdfg/npc -server=<ip:port> -vkey=<web界面中显示的密钥> <以及一些其他参数>
配置文件：
docker run -d --name npc --net=host -v <本机conf目录>:/conf ffdfgdfg/npc -config=/conf/npc.conf
```

## 旧的资料

[内网穿透相关知识](https://juejin.cn/post/7227012113574232121)

- FRP
- NPS
- ZeroTier + ZeroTier moon
- Headscale + Tailscale
- CloudFlare Tunnel 非常好用的内网穿透工具CloudFlare Tunnel

