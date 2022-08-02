all:
	#docker run --net host -d --rm -v ${PWD}:/srv/gitbook hub.iefcu.cn/public/gitbook
	docker run -d --name adam-doc --restart=always \
		-p 4000:4000 \
		-v ${PWD}:/srv/gitbook \
		hub.iefcu.cn/public/gitbook \
		bash -c 'gitbook install && \
		gitbook serve --host 0.0.0.0'

mkdocs:
	#docker run --net host -d --rm -v ${PWD}:/srv/gitbook hub.iefcu.cn/public/gitbook
	docker run -d --name adam-mkdocs-doc --restart=always \
		-p 8000:8000 \
		-v ${PWD}:/data \
		ubuntu_mkdocs \
		bash -c 'cp /data/mkdocs.yml / && mkdocs serve -a 0.0.0.0:8000'
