from update_database import main
def handler(event, context):
   main()
   return {"message": "completed"}