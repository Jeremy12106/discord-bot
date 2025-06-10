from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage
from azure.ai.inference.models import UserMessage
from azure.core.credentials import AzureKeyCredential

from utils.env_loader import GITHUB_API_KEY

class GithubAPI():
    def __init__(self, model):
        self.model = model
        self.api_key = GITHUB_API_KEY

    def get_response(self, prompt, temperature):
        client = ChatCompletionsClient(
            endpoint="https://models.inference.ai.azure.com",
            credential=AzureKeyCredential(self.api_key)
        )

        response = client.complete(
            messages=[
                SystemMessage(content=""""""),
                UserMessage(content=prompt),
            ],
            model=self.model,
            temperature=temperature,
            max_tokens=2048,
        )
        return response.choices[0].message.content