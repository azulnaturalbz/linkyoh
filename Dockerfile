FROM python:3 as builder
# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /linkyoh
WORKDIR /linkyoh

# Install dependencies
COPY requirements.txt /linkyoh/
RUN pip install -r requirements.txt


COPY . /linkyoh/

# Server
EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]



#FROM nginx
#EXPOSE 80
#COPY ./default.conf /etc/nginx/conf.d/default.conf
#COPY --from=builder /linkyoh /usr/share/nginx/html