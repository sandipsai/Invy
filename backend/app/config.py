from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Invoice App API"
    app_version: str = "1.0.0"
    debug: bool = True
    database_url: str = "sqlite:///./invoice.db"
    allowed_origins: str = "http://localhost:5173,http://localhost:4173"
    invoice_prefix: str = "INV"
    invoice_number_width: int = 4
    default_payment_days: int = 30
    default_currency: str = "USD"
    pdf_output_dir: str = "./generated_pdfs"
    tax_label: str = "Tax"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
