# aria2-ui编译armv6版本

我的树莓派是armv6l的cpu，需要编译出来

```bash
docker buildx build  \
  --platform=linux/arm/v6 \
  --build-arg http_proxy=http://proxy.iefcu.cn:20172 \
  --build-arg https_proxy=http://10.20.3.29:20172 \
  -t hub.iefcu.cn/xiaoyun/aria2-ui:armv6 . --push \
```


源码：
https://github.com/wahyd4/aria2-ariang-docker

a8db9193f813b780681c9322f70352e4e220b61e

源码改动点如下：

![](2022-03-01-09-43-50.png)

```diff
diff --git a/install.sh b/install.sh
index 0387194..18468eb 100755
--- a/install.sh
+++ b/install.sh
@@ -1,6 +1,6 @@
 #! /bin/sh -eux

-echo "[INFO] Set variables for $(arch)"
+echo "[INFO] adam Set variables for $(arch)"

 caddy_version=2.4.6
 filebrowser_version=v2.20.1
@@ -14,10 +14,19 @@ case "$(arch)" in
       caddy_file=caddy_${caddy_version}_linux_amd64.tar.gz
       rclone_file=rclone-${rclone_version}-${platform}.zip
      ;;
+   armv6l)
+     platform=linux-armv6
+     caddy_file=caddy_${caddy_version}_linux_armv6.tar.gz
+     rclone_file=rclone-${rclone_version}-linux-arm.zip
+     ;;
+
    armv7l)
-     platform=linux-armv7
-     caddy_file=caddy_${caddy_version}_linux_armv7.tar.gz
-     rclone_file=rclone-${rclone_version}-linux-arm-v7.zip
+     #platform=linux-armv7
+     #caddy_file=caddy_${caddy_version}_linux_armv7.tar.gz
+     #rclone_file=rclone-${rclone_version}-linux-arm-v7.zip
+     platform=linux-armv6
+     caddy_file=caddy_${caddy_version}_linux_armv6.tar.gz
+     rclone_file=rclone-${rclone_version}-linux-arm.zip
      ;;

    aarch64)
```

运行时，
max-upload-limit
dir=/data
file-allocation=prealloc
disable-ipv6=true
/var/log/aria2.log
Ok，不会segment

```bash
podman run -d --name aria2-ui2 \
  -p 80:80 \
  --env ENABLE_RCLONE=false \
  -v /data/aria2-data/:/data \
  wahyd4/aria2-ui
# hub.iefcu.cn/public/aria2-ui
```
