all:
	docker run --net host -d --rm -v ${PWD}:/srv/gitbook hub.iefcu.cn/public/gitbook
