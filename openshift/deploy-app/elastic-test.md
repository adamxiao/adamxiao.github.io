# es插入数据测试

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

## 使用jre容器进行测试

```
docker run -it --rm \
   -v $PWD:/app  -w /app \
   --entrypoint /bin/bash \
   hub.iefcu.cn/public/maven:3.8-jdk-8
```

## 生成测试数据

```
rm -f alert.txt
for ((i=0;i<1000;i++)); do

  cat >> alert.txt << EOF
{"index":{"_index":"alert","_type":"doc"}}
{"annotations": {"message": "数据库使用率大于90%"},"endsAt": "0001-01-01T00:00:00Z","generatorURL": "https://thanos-querier-openshift-monitoring.apps.kcp4.iefcu.cn/graph?g0.expr=gbase_database%7Bcode%3D%22database_used_rate%22%2Cnamespace%3D%22aiops%22%7D+%3E+0.9&g0.tab=1","labels": {"alertname": "数据库使用率大于90%","code": "database_used_rate","id": "aiccdb","instance": "192.168.5.114:19888","job": "jit-metrics-db01","label": "数据库-使用率","service": "jit-metrics-db01","severity": "2","type": "数据库"},"levelCode": "c","startsAt": "2022-08-11T05:09:08.952Z"}
EOF

done

unix2dos alert.txt
```

## 插入es测试

注意修改好密码和es服务地址
```
export passwd="6p51lqy8enu9eD5Mfoa540d9"
export es_url="http://es-test-es-test.apps.kcp1-arm.iefcu.cn/log/_bulk"

install ./alert.txt $HOME

java -jar target/demo-1.0-SNAPSHOT.jar
```


## 附录源码

pom.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>org.example</groupId>
    <artifactId>demo</artifactId>
    <version>1.0-SNAPSHOT</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.4.1</version>
        <relativePath/>
    </parent>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <exclusions>
                <exclusion>
                    <groupId>org.springframework.boot</groupId>
                    <artifactId>spring-boot-starter-tomcat</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
        <dependency>
            <groupId>com.alibaba</groupId>
            <artifactId>fastjson</artifactId>
            <version>1.2.76</version>
        </dependency>
        <dependency>
            <groupId>commons-io</groupId>
            <artifactId>commons-io</artifactId>
            <version>2.8.0</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```

./src/main/resources/application.properties
```
spring.task.scheduling.pool.size=50
spring.task.execution.pool.max-size=50
```

./src/main/java/com/estest/Application.java
```java
package com.estest;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.io.File;
import java.util.concurrent.atomic.AtomicLong;

@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }


    @Component
    public static class ApplicationRunner implements CommandLineRunner {

        private final Logger logger = LoggerFactory.getLogger(ApplicationRunner.class);

        @Override
        public void run(String... args) throws Exception {
            //insertEs("data.txt");
            insertEs("alert.txt");
        }

        private void insertEs(String fileName) throws Exception {
            RestTemplate restTemplate = new RestTemplate();
            String root = System.getProperty("user.dir");
            File file = new File(root + "/" + fileName);
            byte[] bytes = FileUtils.readFileToByteArray(file);
            HttpHeaders headers = new HttpHeaders();
			String passwd = System.getenv("passwd");
			String es_url = System.getenv("es_url");
            headers.setBasicAuth("elastic", passwd);
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> request = new HttpEntity<>(new String(bytes), headers);
            long start = System.currentTimeMillis();
            AtomicLong tmp = new AtomicLong(0);
            for (int i = 0; i < 10; i++) {
                new Thread(() -> {
                    while (true) {
                        try {
                            JSONObject object = restTemplate.postForObject(es_url, request, JSONObject.class);
                            //JSONObject object = restTemplate.postForObject("http://es-test2-es-test2.apps.kcp5.iefcu.cn/log/_bulk", request, JSONObject.class);
                            if (object != null) {
                                JSONArray items = object.getJSONArray("items");
                                Long total = items.getJSONObject(items.size() - 1).getJSONObject("index").getLong("_seq_no");
                                tmp.set(tmp.get() + 1000);
                                long end = (System.currentTimeMillis() - start) / 1000 != 0 ? (System.currentTimeMillis() - start) / 1000 : 1;
                                logger.info("共：{}条,已插入：{}条,执行时间：{}s,平均：{}/s", total, tmp.get(), end, tmp.get() / end);
                            }
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                }).start();

            }
        }
    }
}
```
