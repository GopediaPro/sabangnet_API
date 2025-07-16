from pydantic import BaseModel, ConfigDict
from models.mall_certification_handling.mall_certification_handling import MallCertificationHandling

class MallCertificationHandlingDto(BaseModel):
    id: int
    shop_code: str
    certification_detail_id: int
    before_certification_field: str
    final_certification_field: str
    
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, mall_certification_handling: MallCertificationHandling):
        return cls(
            id=mall_certification_handling.id,
            certification_detail_id=mall_certification_handling.certification_detail_id,
            shop_code=mall_certification_handling.shop_code,
            before_certification_field=mall_certification_handling.before_certification_field,
            final_certification_field=mall_certification_handling.final_certification_field
        )
