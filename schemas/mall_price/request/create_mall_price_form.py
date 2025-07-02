from pydantic import BaseModel, Field


class CreateMallPriceForm(BaseModel):
    product_nm: str = Field(..., description="상품코드")
