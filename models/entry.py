# models/entry.py

from dataclasses import dataclass
import json
import time
from urllib.parse import urlparse


def normalize_domain(url_or_domain: str) -> str:
    if "://" in url_or_domain:
        parsed = urlparse(url_or_domain)
        return parsed.netloc.lower()
    return url_or_domain.lower()


@dataclass
class VaultEntry:
    site: str
    username: str
    password: str
    notes: str = ""
    domain: str = ""
    last_used: float = 0.0

    def __post_init__(self):
        if not self.domain:
            self.domain = normalize_domain(self.site)

    def touch(self):
        self.last_used = time.time()

    def serialize(self) -> bytes:
        return json.dumps(self.__dict__).encode("utf-8")

    @staticmethod
    def deserialize(data: bytes) -> "VaultEntry":
        obj = json.loads(data.decode("utf-8"))
        return VaultEntry(**obj)
