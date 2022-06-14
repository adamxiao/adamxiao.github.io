# docker 信任私有证书

## skopoe信任私有证书

```bash
sudo mkdir -p  /etc/docker/certs.d/quay.kcp.cn:9443
sudo scp root@10.90.3.165:/home/data/registry/ssl.cert ssl.crt

sudo skopeo login quay.kcp.cn:9443
sudo skopeo list-tags docker://quay.kcp.cn:9443/kcp/openshift4-aarch64
```

## podman 信任私有证书

```bash
mkdir -p /etc/containers/certs.d/quay.iefcu.cn:9443
cp /root/ssl.cert /etc/containers/certs.d/quay.iefcu.cn:9443/ssl.crt
```

## docker信任私有证书

```
/etc/docker/certs.d/quay.kcp.cn:9443/ssl.crt
```
