"""Settings from the environment (or a local .env file). Nothing secret is ever committed."""
import os
import re
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            v = v.strip()
            if v and v[0] in "\"'" and v.find(v[0], 1) > 0:
                v = v[1:v.find(v[0], 1)]  # quoted: keep what's inside, drop any trailing comment
            else:
                v = re.split(r"\s+#", v, maxsplit=1)[0]  # unquoted: " # ..." is a comment
            os.environ.setdefault(k.strip(), v)


@dataclass(frozen=True)
class Settings:
    base_url: str
    data_dir: Path
    price_cents: int
    creem_api_key: str
    creem_product_id: str
    creem_webhook_secret: str
    creem_api_base: str
    resend_api_key: str
    resend_from: str
    admin_password: str
    fake_payments: bool

    @property
    def payments_ready(self) -> bool:
        return bool(self.creem_api_key and self.creem_product_id and self.creem_webhook_secret)

    @property
    def email_ready(self) -> bool:
        return bool(self.resend_api_key and self.resend_from)


def load() -> Settings:
    _load_dotenv()
    environment = os.environ.get("ENVIRONMENT", "production").strip().lower()
    if environment not in ("production", "development"):
        raise ValueError(f"ENVIRONMENT must be 'production' or 'development', not {environment!r}")
    key = os.environ.get("CREEM_API_KEY", "")
    default_base = "https://test-api.creem.io" if key.startswith("creem_test_") else "https://api.creem.io"
    return Settings(
        base_url=os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/"),
        data_dir=Path(os.environ.get("DATA_DIR", "data")),
        price_cents=int(os.environ.get("PRICE_CENTS", "999")),
        creem_api_key=key,
        creem_product_id=os.environ.get("CREEM_PRODUCT_ID", ""),
        creem_webhook_secret=os.environ.get("CREEM_WEBHOOK_SECRET", ""),
        creem_api_base=os.environ.get("CREEM_API_BASE", default_base).rstrip("/"),
        resend_api_key=os.environ.get("RESEND_API_KEY", ""),
        resend_from=os.environ.get("RESEND_FROM", ""),
        admin_password=os.environ.get("ADMIN_PASSWORD", ""),
        fake_payments=environment == "development",
    )
