# Kyouka: a simple and powerful music bot for KaiHeiLa, it is easy to use and develop.

FROM python:3.9-buster

LABEL maintainer="zhangshuyang@outlook.com"

ENV PYTHONIOENCODING=utf-8

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /Kyouka

COPY requirements.txt /Kyouka
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt && \
    rm -rf /tmp/*

COPY ./app /Kyouka/app
COPY ./startup.py /Kyouka

CMD ["python", "startup.py"]