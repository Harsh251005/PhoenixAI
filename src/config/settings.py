import os

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME")

settings = Settings()