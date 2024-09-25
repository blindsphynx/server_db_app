FROM ubuntu:22.04

RUN apt-get update &&  \
    apt-get install -y git  \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip

RUN git clone https://github.com/blindsphynx/server_db_app.git
COPY ./ .
RUN pip3 install -r requirements.txt

WORKDIR /src/server

RUN chmod +x main.py
RUN apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["python3", "main.py"]
