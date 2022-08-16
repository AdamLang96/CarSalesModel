FROM python:3.10-slim-buster

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENV FLASK_APP="deployment/server"

EXPOSE 8080/TCP

ENTRYPOINT ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=8080"]

