FROM python:3.7
COPY ./app /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN  pip install -r requirements.txt\
     gunicorn -w 4 -b 0.0.0.0:80 run:myapp