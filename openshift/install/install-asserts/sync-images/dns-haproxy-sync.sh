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

cat > image-sync-list.json << EOF
{
"${src_hub}/xiaoyun/keepalived:latest":"${dst_hub}/kcp/keepalived"
,"${src_hub}/xiaoyun/dnsmasq:latest":"${dst_hub}/kcp/dnsmasq"
,"${src_hub}/public/haproxy:lts-alpine":"${dst_hub}/kcp/haproxy"
,"${src_hub}/public/registry:2":"${dst_hub}/kcp/registry"
}
EOF

image-syncer --proc=6 --auth=./image-sync.json --images=./image-sync-list.json --namespace=public \
--registry=hub.iefcu.cn --retries=3
