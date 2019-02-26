京东店铺主页html中都含有`vender_id`，
利用wget和sed过滤得到vender_id

```bash
#!/bin/bash

shop_url=$1
admin_uin=$2
old_vender_id=$3

wget -O adam.html "$shop_url" >/dev/null 2>/dev/null
vender_id=`grep '<input type="hidden" id="vender_id"' adam.html | sed -e 's/.*value="//' | sed -e 's/".*$//'`
#echo "$vender_id\t$admin_uin\t$old_vender_id\t$shop_url"
echo "$vender_id    $shop_url"
```
