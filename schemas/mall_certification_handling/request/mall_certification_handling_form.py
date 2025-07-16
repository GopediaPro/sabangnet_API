from pydantic import BaseModel

class MallCertificationHandlingForm(BaseModel):
    shop_code: str
    certification_detail_id: int
    final_certification_field: str

