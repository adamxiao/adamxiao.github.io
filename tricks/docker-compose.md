# docker-compose用法

## 基本用法

举例一个haproxy的docker-compose.yaml配置文件
```yaml
version: '3.2'
services:
  haproxy:
    image: hub.iefcu.cn/public/haproxy:lts
    container_name: haproxy
    restart: always
    user: root
    network_mode: host
    volumes:
      - ./config/:/etc/haproxy/
      - /etc/localtime:/etc/localtime:ro
    cap_add:
      - ALL
    privileged: true
    command: ["-f", "/etc/haproxy/haproxy.cfg"]
    logging:
      driver: json-file
      options:
        max-file: '3'
        max-size: 100m
```

## 网络互联方面

```yaml
alias: xxx
```