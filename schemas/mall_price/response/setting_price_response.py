from pydantic import BaseModel
from typing import List, Dict

class SettingPriceResponse(BaseModel):
    success: bool
    message: str
    xml_file_path: str
    processed_count: int
    success_items: List[Dict[str, str]]
    failed_items: List[Dict[str, str]]