# 利用Minio搭建私有图床

## xxx

估计是版本 RELEASE.2022-05-08T23-50-31Z

```bash
docker run -itd --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e "MINIO_ROOT_USER=adam" \
  -e "MINIO_ROOT_PASSWORD=password" \
  -v /data/minio/data:/data \
  -v /data/minio/config:/root/.minio \
  minio/minio server /data --console-address ":9001"
```

```bash
docker run -itd -p 9000:9000 \
  --name minio1 \
  -v /data/minio/data:/data \
  -v /data/minio/config:/root/.minio \
  -e "MINIO_ACCESS_KEY=adam" \
  -e "MINIO_SECRET_KEY=password" \
  minio/minio server /data
```

其中/mnt/minio/data和/mnt/minio/config是你的数据挂载目录和配置文件所在目录，这个根据自己需求设置就可以了。
命令执行成功后，打开浏览器，输入localhost:9999就可以访问到Minio的管理后台，输入accessKey和secretKey即可进入。

## 使用图床

### vscode使用图床

* gitee?(github也是一类的) => 后续可能考虑
* PicGo插件?

#### vscode-minio-picman

[写了个适用于vscode的minio图床客户端插件 vscode-minio-picman](https://www.cnblogs.com/laggage/p/15742983.html)

=> 报错: Invalid endPoint 10.20.1.99:9001 (9000端口也报错)
http://10.20.1.99:9000
=> 配置了域名https之后可以了, https://oss.iefcu.cn

为什么不用picgo
看了下picgo是好像需要通过插件支持minio, picgo的vscode的插件好像暂时还不支持picgo插件系统.

不过很感谢vscode-picgo, 获取剪贴板图片的代码抄的就是这个项目的, 让我省了很多时间和精力 🙏

#### PicGo

支持配置使用github仓库?

[使用VScode + PicGo 写markdown 以及github图片加载不出的问题 原创](https://blog.51cto.com/luweir/4878704)

[vscode 截图上传图床](https://juejin.cn/post/6844904015776448520)

[不要再使用Gitee 当图床了，官方已经开启防盗链了-爱代码爱编程](https://icode.best/i/53153746184654)


#### Paste Image

这个插件只保存图片到本地


## 参考资料

* [利用Minio搭建私有图床](https://www.naeco.top/2020/08/11/private-oss-for-image/)
* [minIO官网 - docker搭建](https://docs.min.io/docs/minio-docker-quickstart-guide)
