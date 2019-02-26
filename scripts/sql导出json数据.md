直接用sql语句，用sql的concat函数链接，简单处理

```bash
#!/bin/bash

mysql -s -h $IP -P $PORT -u$USER_NAME -p$PASSWD > /tmp/adam.json <<EOF
SELECT
     CONCAT("{",
           "\"tag\":\"",FtoId,"\",",
           "\"name\":\"",FtoName,"\",",
           "\"other_tag\":",FfromId,",",
           "\"other_name\":\"",FfromName,"\"",
     "},")
AS json FROM test.t_qqshp_tagsrelation WHERE Ffrom = 1;
EOF

sed -e '1i[' -e '$s#,$##' -e '$a]' -i /tmp/adam.json
```
