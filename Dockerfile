FROM python:2.7-stretch

WORKDIR /develop
VOLUME /develop

COPY requirements.txt /develop/requirements.txt
RUN pip install -r requirements.txt

EXPOSE 1072

CMD python run.py
