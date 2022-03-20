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

使用其他容器的网络
```yaml
network_mode: "container:bastion"
```

配置独立ip地址
```yaml
version: '3.4'
services:
  nginx:
    image: hub.iefcu.cn/public/nginx:alpine
    container_name: install-nginx
    restart: always
    hostname: install-nginx
    volumes:
      - /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime:ro
      - /data/install-nginx/install:/usr/share/nginx/html
      - /data/install-nginx/conf.d/:/etc/nginx/conf.d/
    networks:
      macvlan-net:
        #ipv4_address: 192.168.100.100
        ipv4_address: 10.20.1.106
    logging:
      driver: json-file
      options:
        max-file: '3'
        max-size: 100m

networks:
   macvlan-net:
      external:
         name: macvlan-net

#networks:
#  macvlan-net:
#    driver: macvlan
#    driver_opts:
#      parent: enp1s0f0
#    ipam:
#      driver: default
#      config:
#        - subnet: 192.168.100.1/24
#          gateway: 192.168.100.1
```
