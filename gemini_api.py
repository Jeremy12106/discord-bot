import os
import google.generativeai as genai
from dotenv import load_dotenv
import absl.logging

absl.logging.set_verbosity('fatal')
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"


def get_response(text):
  
  load_dotenv(override=True)
  api_key=os.getenv('GOOGLE_API_KEY')
  genai.configure(api_key=api_key)
  model = genai.GenerativeModel('gemini-1.5-flash')
  
  prompt = f"[用繁體中文回答] {text}"
  response = model.generate_content(prompt)
  return response.text

