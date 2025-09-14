"""
Ecount Excel Sale DTOs
이카운트 Excel 판매 관련 DTO
"""

from pydantic import BaseModel
from typing import Optional


class EcountSaleExcelRequestDto(BaseModel):
    """이카운트 판매 Excel 업로드 요청 DTO"""
    
    sheet_name: Optional[str] = "1_판매입력"
    template_code: str = "okmart_erp_sale_ok"
    clear_existing: Optional[bool] = False
    is_test: Optional[bool] = True
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "data": {
                        "sheet_name": "1_판매입력",
                        "template_code": "okmart_erp_sale_ok",
                        "clear_existing": False,
                        "is_test": True
                    },
                    "metadata": {
                        "request_id": "lyckabc"
                    }
                }
            ]
        }
    }
