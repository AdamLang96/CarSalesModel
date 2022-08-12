FROM python:3.10-slim-buster

WORKDIR /app
RUN mkdir my-model
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV MODEL_DIR=/app/my-model
CMD ["python3", "model_train_pipeline.py"]


