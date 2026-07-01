import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME")
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    GENERATED_PROJECTS_DIR = PROJECT_ROOT / Path("generated_projects")


settings = Settings()
