import os
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from utils.env_loader import GEMINI_API_KEY

os.environ["GRPC_VERBOSITY"] = "NONE"
os.environ["GLOG_minloglevel"] = "3"

class GeminiAPI():
    def __init__(self, model):
        self.model = model
        self.api_key = GEMINI_API_KEY
        genai.configure(api_key=self.api_key)

    def get_response(self, prompt, temperature):
        model = genai.GenerativeModel(self.model)
        generation_config = GenerationConfig(temperature=temperature)
        response = model.generate_content(prompt, generation_config=generation_config, safety_settings = 'BLOCK_NONE')
        
        return response.text
    
