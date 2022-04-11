#!/bin/bash

# 关键字《shell解析yaml》
# refer https://www.itranslater.com/qa/details/2130896039891698688
function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

eval $(parse_yaml ./install-config.yaml.bak)
# 需要确保metadata_name等不为空
if [[ "" == "${metadata_name}" ]]
then
    echo parse metadata name empty!
    exit 1
fi


# eg. kcp1.iefcu.cn
dir=${metadata_name}.${baseDomain}
echo "=> 0. start processing cluster $dir ..."
if [[ -a $dir ]];
then
    echo "backing old config $dir ..."
    mkdir -p delete
    mv $dir "delete/${dir}.bak.$(date +%s)"
fi

# 1. 生成点火文件
echo "=> 1. generate ignition files ..."
mkdir $dir && cd $dir
cp -f ../install-config.yaml.bak ./install-config.yaml
cp -f ../install-config.yaml.bak ./install-config.yaml.bak

../openshift-install create manifests
../openshift-install create ignition-configs

# 2. 拷贝点火文件到http服务器中去
echo "=> 2. copy ignition files to http server ..."
ign_dir=../../install-nginx/install/$dir
if [[ -a $ign_dir ]]
then
    rm -rf $ign_dir
    echo "remove old ignition files $ign_dir ..."
fi
mkdir $ign_dir

cp -f *.ign $ign_dir
chmod 644 $ign_dir/*.ign

# 3. 其他处理
mkdir -p $HOME/.kube
cp -f ./auth/kubeconfig $HOME/.kube/config

