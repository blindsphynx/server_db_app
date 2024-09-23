FROM ubuntu:22.04

RUN apt-get update &&  \
    apt-get install -y git  \
    && apt-get install -y python3 \
    && apt-get install python-pip

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts

COPY /home/vilka/.ssh/id_rsa.pub /root/.ssh/id_rsa.pub
RUN chmod 600 /root/.ssh/id_rsa.pub

RUN git clone git@github.com:blindsphynx/http_server_test.git
RUN pip install requirements.txt

WORKDIR /src/server

CMD python3 main.py
