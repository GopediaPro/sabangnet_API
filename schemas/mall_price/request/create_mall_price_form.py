from pydantic import BaseModel, Field


class CreateMallPriceForm(BaseModel):
    products_nm: str = Field(..., description="상품코드")
