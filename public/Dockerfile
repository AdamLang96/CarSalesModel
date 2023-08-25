FROM python:3.9-slim

WORKDIR /src/app
COPY requirements.txt  /src/app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
    
COPY stream_lit.py /src/app
EXPOSE 80
EXPOSE 8080
ENTRYPOINT [ "streamlit", "run",  "stream_lit.py", "--server.port=80", "--server.address=0.0.0.0"] 


