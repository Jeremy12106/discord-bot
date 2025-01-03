import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(override=True)
os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"

class GeminiAPI():
    def __init__(self, gemini_model='gemini-1.5-flash'):
        self.gemini_model = gemini_model
        self.api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=self.api_key)

    def get_response(self, prompt):
        model = genai.GenerativeModel(self.gemini_model)   # gemini-1.5-flash
        response = model.generate_content(prompt, safety_settings = 'BLOCK_NONE')
        
        return response.text
    
