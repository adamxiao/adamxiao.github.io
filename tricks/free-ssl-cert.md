# let's encryption免费申请https证书

## 通过dnspod密钥申请通用证书

参考: [腾讯云 DNSPod 域名 API 申请 Let’s Encrypt 泛域名 SSL 证书过程记录](https://cloud.tencent.com/developer/article/1117551)

#### 1. 准备工作

```
#centos系列
yum update && yum install curl -y && yum install cron -y && yum install socat -y
#ubuntu系列
apt-get update && apt-get install curl -y && apt-get install cron -y && apt-get install socat -y
```

目前我使用一个centos容器处理
```
docker run -it --name cert-req centos:7 bash
```

#### 2. 安装 ACME.SH

```
curl https://get.acme.sh | sh
```

#### 3. 获取域名 API

```
export DP_Id=257832
export DP_Key=xxxxxx
```

获取域名密钥方法:

* 1、腾讯云域名默认使用 DNSPod.cn 做解析，没有 DNSPod 账号要去注册一个，然后把要申请证书的域名使用 DNSPod 的 NS 服务器解析。
* 2、创建 API，用户中心->安全设置->创建Token。要注意的是弹出窗口显示完整的 Token，必须复制保存。因为只显示这一次，如果没记住，那就删除这个再重新创建一个。

#### 4. 签发证书

最终签发的证书文件在/root/.acme.sh/域名文件夹中
```
~/.acme.sh/acme.sh --issue --dns dns_dp --register-account -m iefcuxy@gmail.com -d iefcu.cn -d *.iefcu.cn
~/.acme.sh/acme.sh --issue --dns dns_dp -d iefcu.cn -d *.iefcu.cn
```

#### 5. TODO: 证书自动更新?

容器里面的cron会生效吗?
```
43 0 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
/root/.acme.sh/acme.sh --cron --home /root/.acme.sh/
```

## 其他旧的资料

https://docs.qq.com/doc/DZnF4Zklja29aUlZn
