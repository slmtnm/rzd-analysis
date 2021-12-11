FROM python:3.10-buster

WORKDIR /app
COPY . /app

RUN pip install pipenv
RUN cd /app && pipenv install && pipenv install -d

ENTRYPOINT [ "pipenv", "run", "python", "-m", "collect" ]