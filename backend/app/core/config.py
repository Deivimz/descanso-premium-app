"""
config.py — Configuración centralizada del proyecto con pydantic-settings.

Lee las variables de entorno (desde el archivo .env a través de docker-compose)
y las expone como atributos tipados del objeto `settings`.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Aplicación ────────────────────────────────────────────────────────────
    app_name: str = "Descanso Premium API"
    environment: str = "development"
    debug: bool = True

    # ── MongoDB ───────────────────────────────────────────────────────────────
    mongo_url: str | None = None
    mongo_root_user: str = "admin"
    mongo_root_password: str = "secret1234"
    mongo_db_name: str = "descanso_db"
    mongo_host: str = "mongodb"          # nombre del servicio en docker-compose
    mongo_port: int = 27017

    # ── JWT (Paso 5) ──────────────────────────────────────────────────────────
    secret_key: str = "changeme_supersecret_key_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def mongo_uri(self) -> str:
        """Construye la cadena de conexión de MongoDB a partir de las variables."""
        if self.mongo_url:
            return self.mongo_url
        return (
            f"mongodb://{self.mongo_root_user}:{self.mongo_root_password}"
            f"@{self.mongo_host}:{self.mongo_port}/{self.mongo_db_name}"
            f"?authSource=admin"
        )


# Instancia singleton — se importa en toda la app como: from app.core.config import settings
settings = Settings()
