"""DOCSTRING"""
from io import BytesIO
import boto3
# s3 = boto3.client('s3')
from sqlalchemy import create_engine, text
import pandas as pd
# # with open("data/pickled_models/2022-08-10_model.pkl", 'rb') as f:
# #     s3.upload_fileobj(f, 'carsalesmodel', 'newmodel.pkl')


# s3_client = boto3.client('s3')
# s3_response_object = s3_client.get_object(Bucket='carsalesmodel', Key='newmodel.pkl')
# object_content = s3_response_object['Body'].read()
# print(object_content)


URI = """postgresql://codesmith:TensorFlow01?@cardata.ceq8tkxrvrbb.us-west-2.rds.amazonaws.com:5432/postgres"""
engine = create_engine(URI)
data = pd.read_sql_table("CarsBidData", con=engine)
print(data.shape)