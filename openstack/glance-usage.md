# openstack glance使用

## 上传镜像

关键字《openstack command line upload-to-image》

https://www.mirantis.com/blog/openstack-user-tip-add-new-image-openstack/
```
glance --os-image-api-version 2 image-create --architecture x86_64c\
 --protected False --min-disk 1 --disk-format qcow2 --min-ram 256 \
 --file ./cirros-0.3.4-x86_64-disk.img
```

https://creodias.eu/-/how-to-upload-your-custom-image-using-openstack-cli-
```
openstack image create --disk-format qcow2 --container-format bare \
  --private --file ./custom_image.qcow2 the_name_of_custom_image
=> 验证ok
openstack image create --disk-format qcow2 --container-format bare \
  --public --file ./centos63.qcow2 centos63-image
```

额外参数
- --disk-format <disk-format>
- --min-disk <disk-gb>
- --min-ram <ram-mb>

#### 通过快照创建镜像

https://www.vinchin.com/en/blog/create-upload-image-openstack.html

Create image from snapshot
You can create an image from a powered-off OpenStack instance and this snapshot can be used to migrate the instance.

1. Take a snapshot:
```
$ openstack server image create --name myInstanceSnapshot myInstance
```

2. Import the snapshot to new environment:
```
openstack image create --container-format bare --disk-format qcow2 \
  --file snapshot.raw myInstanceSnapshot
```

## 下载镜像

https://www.linuxtechi.com/upload-download-cloud-images-in-openstack/
```
glance image-download –file <Name-of-Cloud-Image> –progress  <Image_ID>
glance image-download --file RHEL-6_6 --progress  c0247a08-6a68-4bd2-ae3e-ca0e8f654dca
=> 验证可以
```

## 参考资料

- [openstack doc - Upload image into glance](https://docs.openstack.org/murano/yoga/reference/appendix/articles/image_builders/upload.html)
