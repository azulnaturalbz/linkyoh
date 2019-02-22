FROM python:3-alpine
# Set environment varibles
MAINTAINER Silvatech

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#Creating Operating Requirements
RUN mkdir /linkyoh
WORKDIR /linkyoh
COPY . /linkyoh/

#Installing Requirements
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

#Creating User
RUN adduser -D user
USER user

#Start Up Command
CMD python manage.py makemigrations
CMD python manage.py migrate
CMD exec gunicorn linkyoh.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Server
EXPOSE 8000
