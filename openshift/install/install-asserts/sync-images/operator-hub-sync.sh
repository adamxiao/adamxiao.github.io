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

#,"${src_hub}/public/redhat-operator-index:v4.9":"${dst_hub}/kcp/redhat-operator-index:v4.9"

cat > image-sync-list.json << EOF
{
"${src_hub}/kcp/kylin-operator-index:v4.9":"${dst_hub}/kcp/kylin-operator-index:v4.9"
,"${src_hub}/kcp/metallb-operator-bundle":"${dst_hub}/kcp/metallb-operator-bundle"
,"${src_hub}/kcp/metallb-rhel8-operator":"${dst_hub}/kcp/metallb-rhel8-operator"
,"${src_hub}/kcp/metallb-rhel8":"${dst_hub}/kcp/metallb-rhel8"
}
EOF

image-syncer --proc=6 --auth=./image-sync.json --images=./image-sync-list.json --namespace=public \
--registry=hub.iefcu.cn --retries=3
