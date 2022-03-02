FROM hub.iefcu.cn/xiaoyun/gitbook

ADD . /srv/gitbook
# 安装gitbook插件
RUN /usr/local/bin/gitbook install

EXPOSE 4000

CMD /usr/local/bin/gitbook serve
