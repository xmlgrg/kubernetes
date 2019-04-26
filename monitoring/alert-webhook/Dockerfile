FROM alpine:latest
WORKDIR /webhook-dingding
COPY . /webhook-dingding/
RUN apk update && \
    apk add curl python3 && \
    pip3 install flask requests  requests -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
EXPOSE 80
CMD ["/bin/sh","run.sh"]
