# auth/sso.py
from fastapi_sso.sso.github import GithubSSO
from config import settings
import os

# Создаем глобальный экземпляр SSO
def create_github_sso() -> GithubSSO:
    
    client_id = os.getenv("GITHUB_CLIENT_ID") or settings.GITHUB_CLIENT_ID
    client_secret = os.getenv("GITHUB_CLIENT_SECRET") or settings.GITHUB_CLIENT_SECRET
    redirect_uri = os.getenv("GITHUB_REDIRECT_URI") or settings.GITHUB_REDIRECT_URI
    
    if not client_id or not client_secret:
        raise ValueError(
            "GitHub OAuth не настроен. "
            "Установите GITHUB_CLIENT_ID и GITHUB_CLIENT_SECRET в .env файле"
        )
    
    return GithubSSO(
        client_id=client_id,
        client_secret=client_secret, 
        redirect_uri=redirect_uri,
        allow_insecure_http=True
    )

# Глобальный экземпляр
github_sso = create_github_sso()