# rabbitmq消息队列使用

init_ksvd_rabbitmq.py
=> bind exchange and queue 失败
rabbit_mq_cli.sh

## FAQ

#### 跟踪消息

注意需要开启guest用户, 还要赋予权限
(ksvd 2节点集群, 还必须在master节点上监控?)

/var/tmp/rabbitmq-tracing/test.log

https://blog.csdn.net/qq_41376740/article/details/126530526
```
rabbitmq-plugins enable rabbitmq_tracing
rabbitmqctl trace_on
```

日志跟踪模式
```
跟踪xxx日志
publish.#

跟踪deliver日志?
deliver.#

跟踪指定队列?
#.myqueue
```

#### 调试日志

/var/log/rabbitmq/rabbit@managenode8.log
```
=INFO REPORT==== 5-Feb-2023::09:42:22 ===
Enabling tracing for vhost '/ksvd-mc'

=ERROR REPORT==== 5-Feb-2023::09:42:22 ===
webmachine error: path="/api/traces/%2Fksvd-mc/test1"
"Bad Request"
```

## 参考资料

超详细的RabbitMQ入门，看这篇就够了！
https://developer.aliyun.com/article/769883

rabbitMq消息消费日志rabbitmq_tracing
https://blog.csdn.net/github_38924695/article/details/102460387

https://www.51cto.com/article/713038.html
把 RabbitMQ 讲的那叫一个透彻

