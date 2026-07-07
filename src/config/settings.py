import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()


class Settings:
    """Application configuration."""

    def __init__(self) -> None:
        self.OPENAI_API_KEY: SecretStr = SecretStr(
            self._get_env("OPENAI_API_KEY")
        )
        self.OPENAI_MODEL_NAME: str = self._get_env("OPENAI_MODEL_NAME")

        self.PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
        self.GENERATED_PROJECTS_DIR: Path = self.PROJECT_ROOT / "generated_projects"

        self.llm: ChatOpenAI = ChatOpenAI(
            api_key=self.OPENAI_API_KEY,
            model=self.OPENAI_MODEL_NAME,
        )

    @staticmethod
    def _get_env(name: str) -> str:
        """Return an environment variable or raise a helpful error."""
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Environment variable '{name}' is not set.")
        return value


settings = Settings()
