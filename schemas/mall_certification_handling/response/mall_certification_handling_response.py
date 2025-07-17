from pydantic import BaseModel
from schemas.mall_certification_handling.mall_certification_handling_dto import MallCertificationHandlingDto


class MallCertificationHandlingResponse(BaseModel):
    shop_code: str
    certification_detail_id: int
    before_certification_field: str
    final_certification_info: str

    @classmethod
    def from_dto(cls, dto: MallCertificationHandlingDto):
        return cls(
            shop_code=dto.shop_code,
            certification_detail_id=dto.certification_detail_id,
            before_certification_field=dto.before_certification_field,
            final_certification_info=dto.final_certification_field
        )