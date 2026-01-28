FROM python:3.10

RUN pip install pipenv==2022.8.5


RUN apt-get update
RUN apt-get -y install graphviz && \
    apt-get install -y cargo

ADD . /rest-services
WORKDIR /rest-services

RUN pip install bokeh==2.4.3

RUN pip install gunicorn[gevent]


EXPOSE 5000

CMD gunicorn --worker-class gevent --workers 2 --bind 0.0.0.0:5000 wsgi:app --max-requests 100 --timeout 60 --keep-alive 5 --log-level debug --access-logfile access.log --error-logfile error.log
# CMD gunicorn --bind 127.0.0.1:5000 wsgi --access-logfile access.log --error-logfile error.log