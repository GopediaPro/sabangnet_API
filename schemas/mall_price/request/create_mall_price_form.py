from pydantic import BaseModel, Field


class CreateMallPriceForm(BaseModel):
    compayny_goods_cd: str = Field(..., description="상품코드")
