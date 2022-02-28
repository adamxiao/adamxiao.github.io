all:
	#docker run --net host -d --rm -v ${PWD}:/srv/gitbook hub.iefcu.cn/public/gitbook
	docker run -d --name adam-doc --restart=always \
		-p 4000:4000 \
		-v ${PWD}:/srv/gitbook \
		hub.iefcu.cn/public/gitbook \
		gitbook serve --host 0.0.0.0
