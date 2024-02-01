# v2ray使用

## 基本使用

使用docker-compose
```
version: '3.3'
services:
  proxy:
    image: v2fly/v2fly-core
    volumes:
      - ./config/:/etc/v2ray/
    restart:
          always
    network_mode: host
    command:
    - run
    - -c
    - /etc/v2ray/config.json
```

## 反向代理

[8款内网穿透工具对比](https://alianga.com/articles/nas-contrast)
=> v2ray最快最安全, frp最易使用

关键字《v2ray 构建内网反向代理》

[v2ray 反向代理](https://toutyrater.github.io/app/reverse.html)

![](https://toutyrater.github.io/resource/images/block_of_%20reverse-doko.bmp)

公网服务端配置
```
{  
  "reverse":{  //这是 B 的反向代理设置，必须有下面的 portals 对象
    "portals":[  
      {  
        "tag":"portal",
        "domain":"private.cloud.com"        // 必须和上面 A 设定的域名一样
      }
    ]
  },
  "inbounds": [
    {  
      // 接受 C 的inbound
      "tag":"external", // 标签，路由中用到
      "port":80,
      // 开放 80 端口，用于接收外部的 HTTP 访问 
      "protocol":"dokodemo-door",
        "settings":{  
          "address":"127.0.0.1",
          "port":80, //假设 NAS 监听的端口为 80
          "network":"tcp"
        }
    },
    // 另一个 inbound，接受 A 主动发起的请求  
    {  
      "tag": "tunnel",// 标签，路由中用到
      "port":16823,
      "protocol":"vmess",
      "settings":{  
        "clients":[  
          {  
            "id":"b831381d-6324-4d53-ad4f-8cda48b30811",
            "alterId":64
          }
        ]
      }
    }
  ],
  "routing":{  
    "rules":[  
      {  //路由规则，接收 C 请求后发给 A
        "type":"field",
        "inboundTag":[  
          "external"
        ],
        "outboundTag":"portal"
      },
      {  //路由规则，让 B 能够识别这是 A 主动发起的反向代理连接
        "type":"field",
        "inboundTag":[  
          "tunnel"
        ],
        "domain":[  
          "full:private.cloud.com"
        ],
        "outboundTag":"portal"
      }
    ]
  }
}
```

私网客户端配置
```
{  
  "reverse":{ 
    // 这是 A 的反向代理设置，必须有下面的 bridges 对象
    "bridges":[  
      {  
        "tag":"bridge", // 关于 A 的反向代理标签，在路由中会用到
        "domain":"private.cloud.com" // A 和 B 反向代理通信的域名，可以自己取一个，可以不是自己购买的域名，但必须跟下面 B 中的 reverse 配置的域名一致
      }
    ]
  },
  "outbounds": [
    {  
      //A连接B的outbound  
      "tag":"tunnel", // A 连接 B 的 outbound 的标签，在路由中会用到
      "protocol":"vmess",
      "settings":{  
        "vnext":[  
          {  
            "address":"serveraddr.com", // B 地址，IP 或 实际的域名
            "port":16823,
            "users":[  
              {  
                "id":"b831381d-6324-4d53-ad4f-8cda48b30811",
                "alterId":64
              }
            ]
          }
        ]
      }
    },
    // 另一个 outbound，最终连接私有网盘    
    {  
      "protocol":"freedom",
      "settings":{  
      },
      "tag":"out"
    }    
  ],
  "routing":{   
    "rules":[  
      {  
        // 配置 A 主动连接 B 的路由规则
        "type":"field",
        "inboundTag":[  
          "bridge"
        ],
        "domain":[  
          "full:private.cloud.com"
        ],
        "outboundTag":"tunnel"
      },
      {  
        // 反向连接访问私有网盘的规则
        "type":"field",
        "inboundTag":[  
          "bridge"
        ],
        "outboundTag":"out"
      }
    ]
  }
}
```

## FAQ

#### vmess隧道建立失败

参考: https://github.com/233boy/v2ray/issues/812

配置这个解决
```
export V2RAY_VMESS_AEAD_FORCED=false
```

=> 修改alertID为0即可?

服务端日志
```
i/o timeout > proxy/vmess/encoding: invalid user: VMessAEAD is enforced and a non VMessAEAD connection is received.
You can still disable this security feature with environment variable v2ray.vmess.aead.forced = false
```

#### 反向代理close

原来是vmess客户端没有连接上
=> 配置客户端连接上即可

服务端日志
```
failed to process reverse connection > app/reverse: empty worker list
```

## 参考资料

[v2ray官网文档 - 反向代理](https://www.v2ray.com/chapter_02/reverse.html)

https://guide.v2fly.org/advanced/outboundproxy.html#链式代理转发
