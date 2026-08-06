from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://wh_user:wh_secret@localhost:5432/warehouse_db"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://wh_rabbit:rabbit_secret@localhost:5672/"
    app_env: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()