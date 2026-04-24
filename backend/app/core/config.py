from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    PROJECT_NAME: str = "FasalIQ"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DASHBOARD_USERNAME: str = os.getenv("DASHBOARD_USERNAME", "admin")
    DASHBOARD_PASSWORD: str = os.getenv("DASHBOARD_PASSWORD", "admin123")

    # Databricks MLflow Settings
    DATABRICKS_HOST: str = os.getenv("DATABRICKS_HOST")
    DATABRICKS_TOKEN: str = os.getenv("DATABRICKS_TOKEN")
    DATABRICKS_MODEL_ENDPOINT: str = os.getenv("DATABRICKS_MODEL_ENDPOINT", "fasaliq_crisp_model")


settings = Settings()