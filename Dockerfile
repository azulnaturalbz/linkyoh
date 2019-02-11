FROM python:3 as builder
ENV PYTHONUNBUFFERED 1
RUN mkdir /linkyoh
WORKDIR /linkyoh
COPY requirements.txt /linkyoh/
RUN pip install -r requirements.txt
COPY . /linkyoh/
CMD [ "python", "manage.py runserver 127.0.0.1:8000" ]


FROM nginx
EXPOSE 80
COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /linkyoh /usr/share/nginx/html