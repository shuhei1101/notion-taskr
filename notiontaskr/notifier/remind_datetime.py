from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RemindDateTime:
    before_start: Optional["datetime"] = None
    before_end: Optional["datetime"] = None
