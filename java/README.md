# java使用

编译工程

## 编译jar包

使用了mvn镜像仓库配置编译(可以去除,直接使用外网镜像仓库)
```
docker run -it --rm \
   --env http_proxy=http://proxy.iefcu.cn:20172 \
   --env https_proxy=http://proxy.iefcu.cn:20127 \
   -v $HOME/workspaces/mvn-settings.xml:/usr/share/maven/conf/settings.xml \
   -v $PWD:/app  -w /app \
   hub.iefcu.cn/public/maven:3.8-jdk-8 \
   mvn clean install -Dmaven.test.skip=true
```


## 使用jar包

```
    -D<name>=<value>
                  set a system property

    -cp <class search path of directories and zip/jar files>
    -classpath <class search path of directories and zip/jar files>
    --class-path <class search path of directories and zip/jar files>
                  A : separated list of directories, JAR archives,
                  and ZIP archives to search for class files.
```

```
java -Dlog4j.configurationFile=file:/home/adam/Downloads/smart-license/conf/log4j2.xml \
  -cp /home/adam/Downloads/smart-license/lib/*  \
  org.smartboot.license.server.LicenseServer \
  1d hello 
```
