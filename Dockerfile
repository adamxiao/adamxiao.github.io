FROM node:6-slim

MAINTAINER Adam Xiao <iefcuxy@gmail.com>

ARG VERSION=3.2.1

LABEL version=$VERSION

RUN npm install --global gitbook-cli &&\
        gitbook fetch ${VERSION} &&\
        npm cache clear &&\
        rm -rf /tmp/*

WORKDIR /srv/gitbook

ADD . /srv/gitbook
RUN /usr/local/bin/gitbook install

EXPOSE 4000

CMD /usr/local/bin/gitbook serve
