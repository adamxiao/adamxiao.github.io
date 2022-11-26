# next-terminal使用

## 使用Next Terminal在浏览器中管理你的服务器

使用Next Terminal在浏览器中管理你的服务器
https://www.xiaoz.me/archives/15752

服务器不允许上网并且需要跳板机才能访问？学会使用这个工具，轻松让服务器使用yum。
https://typesafe.cn/posts/4dnat/

普通用户还是使用了guacc, 连接不上ssh
http://10.20.1.99:8088/#/access?assetId=325213cd-8e13-4435-9baf-9155fbc116da&assetName=arm-docker&protocol=ssh
http://10.20.1.99:8088/#/term?assetId=325213cd-8e13-4435-9baf-9155fbc116da&assetName=arm-docker

https://github.com/dushixiang/next-terminal

配置nginx反向代理报错
```
$ docker logs -f next-terminal_next-terminal_1
2022-10-23 16:37:14 ERROR [log.Errorf:114]升级为WebSocket协议失败：websocket: the client is not using the websocket protocol: 'upgrade' token not found in 'Connection' header
echo: http: superfluous response.WriteHeader call from github.com/labstack/echo/v4.(*Response).WriteHeader (response.go:63)
```

按照官方文档配置nginx反向代理, 参考官方文档： https://next-terminal.typesafe.cn/install/reverse-proxy.html
```
location / {
    proxy_pass http://127.0.0.1:8088/;
    proxy_set_header Host      $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $http_connection;
}
```

## docker-compose启动服务

```
version: '3.3'
services:
  guacd:
    image: dushixiang/guacd:latest
    volumes:
      - ./data:/usr/local/next-terminal/data
    restart:
          always
  next-terminal:
    #image: dushixiang/next-terminal:latest
    image: hub.iefcu.cn/xiaoyun/next-terminal:latest
    environment:
      DB: sqlite
      GUACD_HOSTNAME: guacd
      GUACD_PORT: 4822
    ports:
      - "8088:8088"
    volumes:
      - /etc/localtime:/etc/localtime
      - ./data:/usr/local/next-terminal/data
    restart:
      always
```

## 构建镜像

master分支
4ff4d374429d1291c257537973431fb13ac53e5c

```
FROM hub.iefcu.cn/public/node:14 AS nodebuilder

WORKDIR /opt/app-root/src

ADD web .

USER 0

# run the build
RUN npm install
RUN npm run build
```

修正老版本的一个小问题
```
+++ b/web/src/components/asset/MyAsset.js
-                            if (protocol === 'ssh' && sshMode === 'native') {
+                            if (protocol === 'ssh' && (sshMode === 'native' || sshMode === 'naive')) {
```
