# java使用

编译工程

## 反编译class

解压jar包, `unzip xxx.jar`

反编译class文件, `javap xxx.class`
javap -c -v xxx.class

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

## java web

jnlp后缀文件打开方式，安装了jre环境没用

- 1.旧的浏览器支持, 例如kylin 3.3-3B系统自带的firefox
  新版浏览器都不支持了
- 2.手动使用javaws打开, javaws launch.jnlp
  ubuntu 20.04安装javaws, apt install icedtea-netx

自Java 11起，Oracle不再包含Java Web Start和 javaws 工具在其JRE/JDK发行版中

由于安全性和其他考虑，许多现代浏览器已经不再支持NPAPI插件，这意味着它们可能不支持直接在浏览器中运行Java应用程序。在这种情况下，你可以尝试使用支持Java的较旧版本的浏览器
