from dotenv import load_dotenv
load_dotenv()

from lambda_function import lambda_handler

result = lambda_handler(None, None)
print(result)