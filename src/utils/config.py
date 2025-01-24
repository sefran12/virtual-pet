import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class AIConfig:
    def __init__(self, provider="openai"):
        self.provider = provider
        if provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.base_url = None
        elif provider == "google":
            self.api_key = os.getenv("GOOGLE_API_KEY")
            self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def get_client(self):
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def get_model(self):
        if self.provider == "openai":
            return "gpt-4o-mini"
        elif self.provider == "google":
            return "models/gemini-2.0-flash-exp"
