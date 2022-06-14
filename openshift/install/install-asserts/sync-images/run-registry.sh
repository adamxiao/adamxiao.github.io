mkdir -p $PWD/registry
docker run -d --name registry --restart=always \
  -p 5000:5000 \
  -v $PWD/registry:/var/lib/registry \
  hub.iefcu.cn/public/registry:2
