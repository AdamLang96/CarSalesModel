# FROM public.ecr.aws/lambda/python:3.8
FROM python:3.7-slim-buster


# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY requirements.txt  .
RUN pip install --upgrade pip
RUN  pip install -r requirements.txt 
COPY model_train_pipeline.py .
COPY . .
COPY app.py .
CMD [ "python3",  "app.py" ] 
