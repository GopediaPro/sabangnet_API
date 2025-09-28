from pydantic import BaseModel, Field
from typing import Optional
from schemas.integration_request import IntegrationRequest, Metadata


class CreateProductMallValueData(BaseModel):
    compayny_goods_cd: str = Field(..., description="자체 상품 코드", example="test_0920_OFS-LDRS67")
    gubun: str = Field(..., description="구분 (전문가/마스터/1+1)", example="전문몰")
    standard_price: int = Field(..., description="기준 가격", example=37900)
    
    # 선택적 필드들
    mall_prod_name: Optional[str] = Field(None, description="쇼핑몰 상품명", example="테스트 상품")
    mall_prop1_cd: Optional[str] = Field(None, description="쇼핑몰 속성1 코드", example="001")
    buinf_id3: Optional[str] = Field(None, description="사업자 정보 ID3", example="B0000001")
    mall_stock_rate: Optional[str] = Field(None, description="쇼핑몰 재고율", example="100")
    certno: Optional[str] = Field(None, description="인증번호", example="20290909")
    issuedate: Optional[str] = Field(None, description="발급일", example="20290909")
    certdate: Optional[str] = Field(None, description="인증일", example="20290909")
    avlst_dm: Optional[str] = Field(None, description="유효시작일", example="20290909")
    avled_dm: Optional[str] = Field(None, description="유효종료일", example="20290909")
    cert_agency: Optional[str] = Field(None, description="인증기관", example="한국인증원")
    certfield: Optional[str] = Field(None, description="인증분야", example="전자제품")

    class Config:
        from_attributes = True


class CreateProductMallValueForm(IntegrationRequest[CreateProductMallValueData]):
    """ProductMallValue 생성 요청 폼"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "compayny_goods_cd": "test_0920_OFS-LDRS67",
                    "gubun": "전문몰",
                    "standard_price": 37900,
                    "mall_prod_name": "테스트 상품",
                    "mall_prop1_cd": "001",
                    "buinf_id3": "B0000001",
                    "mall_stock_rate": "100",
                    "certno": "20290909",
                    "issuedate": "20290909",
                    "certdate": "20290909",
                    "avlst_dm": "20290909",
                    "avled_dm": "20290909",
                    "cert_agency": "한국인증원",
                    "certfield": "전자제품"
                },  
                "metadata": {
                    "request_id": "lyckabc"
                }
            }
        }
