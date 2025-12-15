import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIEND_ID")
    GITHUB_CLIENT_SECRET: str= os.getenv("GITHUB_CLIEND_SECRET")
    GITHUB_REDIRECT_URI: str = os.getenv('GITHUB_REDIRECT_URI')

settings = Settings()