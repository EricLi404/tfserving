FROM python:3.7

RUN mkdir /s
WORKDIR /s

ADD . .

RUN sed -i "s/deb.debian.org/mirrors.aliyun.com/g;s/security.debian.org/mirrors.aliyun.com/g" /etc/apt/sources.list && \
    apt-get update  && apt-get install -y curl unzip gnupg2 wget && \
    pip config set global.trusted-host mirrors.aliyun.com &&  pip config set global.index-url https://mirrors.aliyun.com/pypi/simple && \
    pip install --upgrade pip && pip install nacos-sdk-python glob2 boto3 toml apscheduler protobuf

RUN echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" |  tee /etc/apt/sources.list.d/tensorflow-serving.list && \
    curl "https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg" |  apt-key add - && \
    apt-get update && apt-get install -y tensorflow-model-server


EXPOSE 8080 8081

ENTRYPOINT ["sh", "/s/start.sh"]
