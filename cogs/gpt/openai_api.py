import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

class OpenaiAPI():
    def __init__(self, openai_model = "gpt-4o-mini"):
        self.openai_model = openai_model
        self.api_key = os.getenv('OPENAI_API_KEY')

    def get_response(self, prompt):
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=self.api_key
        )

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.openai_model,
            temperature=1,
            max_tokens=4096,
            top_p=1
        )
        return response.choices[0].message.content