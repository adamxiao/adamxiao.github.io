src_hub="hub.iefcu.cn"
dst_hub="127.0.0.1:5000"

cat > image-sync.json << EOF
{
    "${src_hub}": {
        "username": "TODO:username",
        "password": "TODO:passwd"
    }
    ,"${dst_hub}": {
        "username": "TODO:username",
        "password": "TODO:passwd"
        ,"insecure": true
    }
}
EOF

# xiaoyun/openshift4-aarch64
# 1. 原始版本: (注意:当时用的原始quay.io的openshift-install)
# hub.iefcu.cn/xiaoyun/openshift4-aarch64:4.9.0-rc.6-arm64
# 2. 0304版本
# jit-0304-console-install-ok
# hub.iefcu.cn/xiaoyun/openshift4-aarch64@sha256:3668ad5942cb4bfdeea526571b267a570ae1a1201843c68c364958ab2ec4af75
# 3. zhouming 0610版本
# quay.kcp.cn:9443/kcp/openshift4-aarch64
# quay.kcp.cn:9443/kcp/kcp-release-4.9.0.4:latest
# => quay.iefcu.cn/kcp/kcp-release-0610:4.9.0-rc.6-arm64

cat > image-sync-list.json << EOF
{
"${src_hub}/kcp/kcp-aarch64-0610":"${dst_hub}/kcp/kcp-aarch64-0610"
}
EOF

image-syncer --proc=6 --auth=./image-sync.json --images=./image-sync-list.json --namespace=public \
--registry=hub.iefcu.cn --retries=3
