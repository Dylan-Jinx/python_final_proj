FROM python:3.9.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN python -m pip install --upgrade pip
RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev -y
RUN  pip install -r requirements.txt
COPY . /code/