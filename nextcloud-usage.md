# nextcloud安装使用

## 安装

参考nextcloud docker: https://github.com/nextcloud/docker

最简单的试用, 一行命令搞定
```
docker run -d -p 8080:80 nextcloud
```

## 使用

手机nextcloud应用无法同步照片，不好用
**关键就是不能同步照片**

发现保存为后台纯文件, 还行
```
root@bd67076ecb58:/var/www/html/data/adam/files# ls Photos/
'23-03-05 13-26-34 8420.jpg'   Birdie.jpg		  Readme.md
'23-03-05 13-29-08 8421.jpg'   Frog.jpg			  Steps.jpg
```

#### 旧的资料

nextcloud网盘安装
可以只用pvc+nextcloud的镜像就安装好，额外组件redis，mysql，php都不用？

https://sre.ink/kubernetes-deploy-nextcloud-disk/
使用了docker-compose，最简单搭建网盘，只用一个镜像即可.
权限不对，遇到了一次，重新删除啥的，就好了，需要注意。这个应该是nextcloud没有适配好k8s的缘故。
也可能是我之前没有scc配置上的缘故！ => 验证delete pod确实可以。！！
