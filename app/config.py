from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Invoice Factoring Platform"
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str
    WEB3_PROVIDER_URL: str
    CONTRACT_ADDRESS: str
    
    class Config:
        env_file = ".env"

settings = Settings()