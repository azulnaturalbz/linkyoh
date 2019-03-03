FROM python:3.7-alpine
# Set environment varibles
MAINTAINER Silvatech

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#Creating Operating Requirements
RUN mkdir /linkyoh
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev && apk --no-cache add jpeg-dev \
        zlib-dev \
        freetype-dev \
        lcms2-dev \
        openjpeg-dev \
        tiff-dev \
        tk-dev \
        tcl-dev \
        harfbuzz-dev \
        fribidi-dev
WORKDIR /linkyoh
COPY . /linkyoh/

#Installing Requirements
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

#Creating User
RUN adduser -D user
USER user

RUN chown -R user /linkyoh/media
RUN chown -R user /linkyoh/static

#Start Up Command
CMD python manage.py makemigrations
CMD python manage.py migrate
CMD exec gunicorn linkyoh.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Server
EXPOSE 8000
