from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = "<PASSWORD>"

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


redis_config = RedisConfig()
