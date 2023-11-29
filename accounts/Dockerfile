FROM python:3.11.6-slim-bullseye
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN mkdir src
ADD . src/
WORKDIR /src

CMD uvicorn main:app --host 0.0.0.0 --port 8000
