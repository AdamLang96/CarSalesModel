import sys
from model_train_pipeline import main
def handler(event, context):
    main()
    return 'Hello from AWS Lambda using Python' + sys.version + '!'   
