# operator应用安装

xxx

elasticsearch这个operator标明不支持arm64, 所以web页面上不能安装？ => 确实是的!
```bash
oc -n openshift-operators get clusterserviceversion -o yaml

    labels:
      olm.api.9337dac30a6def29: provided
      olm.api.e43efcaa45c9f8d0: provided
      olm.copiedFrom: openshift-operators-redhat
      operatorframework.io/arch.amd64: supported
      operatorframework.io/arch.ppc64le: supported
      operatorframework.io/arch.s390x: supported
    name: elasticsearch-operator.5.3.4-13
```
