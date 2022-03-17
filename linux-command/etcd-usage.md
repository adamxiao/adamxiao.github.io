# etcd使用入门

## 

```bash
etcdctl endpoint status -w table
```

输出示例
```
etcdctl endpoint status -w table
{"level":"warn","ts":"2022-03-16T14:49:04.034Z","logger":"etcd-client","caller":"v3/retry_interceptor.go:62","msg":"retrying of unary invoker failed","target":"etcd-endpoints://0x40001568c0/#initially=[https://10.90.3.21:2379;https://10.90.3.22:2379;https://10.90.3.23:2379]","attempt":0,"error":"rpc error: code = DeadlineExceeded desc = latest balancer error: last connection error: connection error: desc = \"transport: Error while dialing dial tcp 10.90.3.21:2379: connect: connection refused\""}
Failed to get the status of endpoint https://10.90.3.21:2379 (context deadline exceeded)
+-------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+-----------------------+
|        ENDPOINT         |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX |        ERRORS         |
+-------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+-----------------------+
| https://10.90.3.22:2379 | 29df313a73c25e0f |   3.5.0 |  212 MB |      true |      false |       372 |   14085303 |           14085303 |                       |
| https://10.90.3.23:2379 | c418a034547ed46f |   3.5.0 |  212 MB |     false |      false |       372 |   14085303 |           14085303 | etcdserver: no leader |
+-------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+-----------------------+
```

## 参考资料

* https://www.kubernetes.org.cn/7569.html