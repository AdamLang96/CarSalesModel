FROM python:3.10-slim-buster

WORKDIR /app
RUN mkdir my-model
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["python3", "train/model_train_pipeline.py"]


