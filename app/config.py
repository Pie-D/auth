import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-access")
    REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "change-me-refresh")
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://app_user:app_pass@mysql:3306/auth_db",
    )


settings = Settings()

