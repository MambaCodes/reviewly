"""Configuration management for the application."""
from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv
import os

class Config(BaseModel):
    """Application configuration."""
    github_token: str
    github_repo_url: str
    deepseek_api_key: str

@lru_cache()
def get_config() -> Config:
    """Get the application configuration."""
    load_dotenv()
    
    return Config(
        github_token=os.getenv("GITHUB_TOKEN", ""),
        github_repo_url=os.getenv("GITHUB_REPO_URL", ""),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", "")
    )
