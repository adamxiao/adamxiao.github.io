cat <<EOF | kubectl apply -f -
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: test1
  namespace: es-test
spec:
  version: 7.16.3
  #image: hub.iefcu.cn/public/elasticsearch:7.16.3
  image: registry.kcp.local:5000/elasticsearch:7.16.3
  http:
    tls:
      selfSignedCertificate:
        disabled: true # 关闭tls
  nodeSets:
  - name: default 
    count: 3 # 部署集群节点数
    config:
      node.store.allow_mmap: false
    volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data # Do not change this name unless you set up a volume mount for the data path.
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 5Gi
        storageClassName: slow
EOF
