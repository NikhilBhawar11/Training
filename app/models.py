
from dataclasses import dataclass


@dataclass
class Record:
    fort_name: str
    district: str
    height_ft: float | None
    base_village: str | None
    trek_notes: str | None
    source_url: str
