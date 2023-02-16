FROM python:3.9-slim


# Install the function's dependencies using file requirements.txt
# from your project folder.
WORKDIR /src/app
COPY requirements.txt  /src/app
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install -r requirements.txt 

COPY stream_lit.py /src/app
EXPOSE 8501
CMD [ "streamlit", "run",  "stream_lit.py", "--server.port=8501", "--server.address=0.0.0.0"] 
