# FROM public.ecr.aws/lambda/python:3.8
FROM python:3.7-slim-buster

COPY requirements.txt  .
RUN pip install --upgrade pip
RUN  pip install -r requirements.txt 
COPY . .
CMD ["python3", "model_training.py"]
