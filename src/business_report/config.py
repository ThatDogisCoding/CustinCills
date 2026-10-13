from datetime import date
from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WeekStartDay(str, Enum):
    MONDAY = "monday"
    SUNDAY = "sunday"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database (Phase 3)
    database_url: str = Field(
        default="postgresql+psycopg://localhost:5432/business_report",
        description="SQLAlchemy database URL",
    )

    # Mindbody API (Phase 2)
    mindbody_api_key: str = Field(default="", description="Mindbody API key")
    mindbody_site_id: str = Field(default="", description="Mindbody site ID")
    mindbody_login_email: str = Field(default="", description="Mindbody staff login email")
    mindbody_login_password: str = Field(default="", description="Mindbody staff login password")
    mindbody_login_url: str = Field(
        default="https://signin.mindbodyonline.com/",
        description="Mindbody staff sign-in URL",
    )

    # GoHighLevel API (Phase 2)
    ghl_api_token: str = Field(default="", description="GoHighLevel API token")
    ghl_location_id: str = Field(default="", description="GoHighLevel location ID")

    # Axle API (Phase 2)
    axle_api_key: str = Field(default="", description="Axle API key")
    axle_base_url: str = Field(default="", description="Axle API base URL")

    # Reporting defaults (see docs/business_rules.md)
    report_week_start_day: WeekStartDay = WeekStartDay.MONDAY
    business_timezone: str = Field(default="America/New_York")
    fuzzy_match_threshold: int = Field(default=90, ge=0, le=100)
    output_dir: Path = Field(default=Path("output"))

    def ensure_output_dir(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir


def get_settings() -> Settings:
    return Settings()


class ReportingPeriod:
    """A weekly reporting window (Monday–Sunday by default)."""

    def __init__(self, start: date, end: date):
        if end < start:
            raise ValueError("Reporting period end must be on or after start")
        self.start = start
        self.end = end

    @property
    def label(self) -> str:
        return f"{self.start.isoformat()} to {self.end.isoformat()}"

    def __repr__(self) -> str:
        return f"ReportingPeriod({self.start!r}, {self.end!r})"
