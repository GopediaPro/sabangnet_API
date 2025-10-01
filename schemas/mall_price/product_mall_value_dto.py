from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ProductMallValueDto(BaseModel):

    class Config:
        from_attributes = True

    product_nm: Optional[str] = Field(None, description="상품명")
    product_raw_data_id: int = Field(alias="test_product_raw_data_id", description="product_raw_data ID")
    compayny_goods_cd: Optional[str] = Field(None, description="자체 상품 코드")
    standard_price: Optional[int] = Field(None, description="기준 가격")

    # 새로 추가된 필드들
    batch_id: Optional[str] = Field(None, description="배치 ID")
    gubun: Optional[str] = Field(None, description="구분 (전문가/마스터/1+1)")
    mall_prod_name: Optional[str] = Field(None, description="쇼핑몰 상품명")
    mall_prop1_cd: Optional[str] = Field(None, description="쇼핑몰 속성1 코드")
    buinf_id3: Optional[str] = Field(None, description="사업자 정보 ID3")
    mall_stock_rate: Optional[str] = Field(None, description="쇼핑몰 재고율")
    certno: Optional[str] = Field(None, description="인증번호")
    issuedate: Optional[str] = Field(None, description="발급일")
    certdate: Optional[str] = Field(None, description="인증일")
    avlst_dm: Optional[str] = Field(None, description="유효시작일")
    avled_dm: Optional[str] = Field(None, description="유효종료일")
    cert_agency: Optional[str] = Field(None, description="인증기관")
    certfield: Optional[str] = Field(None, description="인증분야")

    # JSONB 컬럼으로 모든 shop 정보 저장
    shops: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="쇼핑몰별 가격 및 상품명 정보")
