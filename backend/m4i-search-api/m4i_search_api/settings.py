import os
from dataclasses import dataclass
from typing import Dict


def _to_bool(value: str, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() not in {"false", "0", "no", "off"}


@dataclass
class AppSearchSettings:
    base_url: str
    token: str
    timeout_seconds: int
    verify_ssl: bool

    @classmethod
    def from_env(cls) -> "AppSearchSettings":
        base_url = os.getenv("APP_SEARCH_BASE_URL")
        token = os.getenv("APP_SEARCH_TOKEN")
        timeout_seconds = int(os.getenv("APP_SEARCH_TIMEOUT_SECONDS", os.getenv("APP_SEARCH_TIMEOUT", "15")))
        verify_ssl = _to_bool(os.getenv("APP_SEARCH_VERIFY_SSL"), True)

        required: Dict[str, str] = {
            "APP_SEARCH_BASE_URL": base_url,
            "APP_SEARCH_TOKEN": token,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing)}")

        return cls(
            base_url=base_url.rstrip("/"),
            token=token,
            timeout_seconds=timeout_seconds,
            verify_ssl=verify_ssl,
        )


def build_target_url(base_url: str, path: str) -> str:
    clean_base = base_url.rstrip("/")
    clean_path = path.lstrip("/")
    if not clean_path:
        return clean_base
    return f"{clean_base}/{clean_path}"
