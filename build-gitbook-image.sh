# docker build -t hub.iefcu.cn/xiaoyun/adam-doc .

docker buildx build \
	--platform=linux/arm64,linux/amd64 \
	-t hub.iefcu.cn/xiaoyun/adam-doc . --push
