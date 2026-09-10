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
        self.DOCKER_EXECUTOR_IMAGE: str = os.getenv("DOCKER_EXECUTOR_IMAGE", "python:3.12-slim")
        self.DOCKER_NETWORK: str = os.getenv("DOCKER_NETWORK", "none")
        self.DOCKER_MEMORY: str = os.getenv("DOCKER_MEMORY", "256m")
        self.DOCKER_CPUS: str = os.getenv("DOCKER_CPUS", "0.5")
        self.DOCKER_PIDS_LIMIT: int = int(os.getenv("DOCKER_PIDS_LIMIT", "64"))

        self.llm: ChatOpenAI = ChatOpenAI(
            api_key=self.OPENAI_API_KEY,
            model=self.OPENAI_MODEL_NAME,
            service_tier="flex",
        )

    @staticmethod
    def _get_env(name: str) -> str:
        """Return an environment variable or raise a helpful error."""
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Environment variable '{name}' is not set.")
        return value


settings = Settings()
