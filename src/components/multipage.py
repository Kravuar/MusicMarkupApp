from dataclasses import dataclass
from typing import Any


@dataclass
class GotoPayload:
    name: str
    data: Any = None
