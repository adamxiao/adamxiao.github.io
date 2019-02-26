# ssh 反向隧道

```bash
remote_ip=127.0.0.1
local_ip=127.0.0.1
ssh -N -f -L3970:${remote_ip}:3970 user_00@${local_ip} -p 36000

mysql -uusername -ppasswd -h127.0.0.1 -P3970
```
