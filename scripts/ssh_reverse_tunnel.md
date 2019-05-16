# ssh 正向端口转发

```bash
remote_ip=127.0.0.1
local_ip=127.0.0.1
ssh -N -f -L3970:${remote_ip}:3970 user_00@${local_ip} -p 36000

mysql -uusername -ppasswd -h127.0.0.1 -P3970
```

# ssh 反向隧道

```bash
ssh -p 22 -qngfNTR 22345:localhost:22 adam@${remote_ip}
```

# ssh sock5 代理

代理端口1080
```bash
ssh -p 22345 -N -D 127.0.0.1:1080 adam@127.0.0.1
```
