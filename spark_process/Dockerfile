# FROM python:3.10-buster
FROM bde2020/spark-python-template:3.1.1-hadoop3.2

WORKDIR /app
COPY . /app

RUN pip3 install pipenv
RUN cd /app && pipenv install && pipenv install -d

ENTRYPOINT [ "pipenv", "run", "python3", "-m", "spark_processor" ]