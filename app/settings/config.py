from typing import List
from dotenv import load_dotenv
from typing import List
import os
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings



load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY:str = os.getenv("JWT_REFRESH_SECRET_KEY")
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*5*5
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7   # 7 days
    BACKEND_CORS_ORIGINS:List = [
        "http://localhost:3000/"
    ]
    PROJECT_NAME: str = "BEDATER BACKEND"
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")
    REDIS_HOST:str = os.getenv("REDIS_HOST")
    AWS_ACCESS_KEY:str = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY:str = os.getenv("AWS_SECRET_KEY")
    AWS_BUCKET_NAME:str = os.getenv("AWS_BUCKET_NAME")
    AWS_REGION:str = os.getenv("AWS_REGION")
    AVATAR_IMAGE_FOLDER_NAME:str = "avatars_skin"


    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(DATABASE_URL,"DATABASE_URL")
    
    class Config:
        case_sensitive = True
        
settings = Settings()



