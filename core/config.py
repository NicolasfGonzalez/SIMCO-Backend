from pydantic_settings import BaseSettings, SettingsConfigDict  # <- S Mayúscula aquí

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Base App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Aquí también cámbialo a S Mayúscula:
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()