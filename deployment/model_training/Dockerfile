# FROM public.ecr.aws/lambda/python:3.8
FROM python:3.7-slim-buster

COPY requirements.txt  .
RUN pip install --upgrade pip
RUN  pip install -r requirements.txt 
COPY . .
ENV ACCESS_KEY=AKIAWO4VL3W2TJBJLKPD
ENV ACCESS_SECRET=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
ENV REGION=us-west-2
ENV TRAINING_ROUNDS=1
ENV URI=postgresql+psycopg2://postgres:postgres@database-1.c45apqxvtyvo.us-west-2.rds.amazonaws.com/postgres
