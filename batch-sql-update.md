# shell批量alert新增mysql表字段
十库千表，需要脚本批量修改

## 1. 生成要改的库名表名
adam_gen_tb.sh
```bash
#!/bin/bash

db_prefix=${1}
tb_prefix=${2}

> db.list # tb list

for ((i=0;i<10;i++));do
    for ((j=0;j<100;j++));do
        echo ${db_prefix}${i}.${tb_prefix}${j} >> db.list 
    done
done
```

## 2. 批量对所有表新增字段
adam_add_column.sh
```bash
#!/bin/sh

DB_TB_FILE=$1

# db conf
DBIP=${1}
DBPORT=${2}
DBUSER=${3}
DBPASS=${4}


for DB_TB_NAME in `cat $DB_TB_FILE`
do
    echo "process $DB_TB_NAME ..."
    mysql -h$DBIP -P$DBPORT -u$DBUSER -p$DBPASS  << EOF
begin;
ALTER TABLE $DB_TB_NAME ADD Fstatus int(11) COMMENT 'action status: 0 valid; 1 invalid';
commit;
exit
EOF
    if [[ $? -ne 0 ]]; then
        >&2 echo "process failed $DB_TB_NAME"
    fi
done
```

操作批量新增字段
```bash
sh adam_add_column.sh < db.list
```
