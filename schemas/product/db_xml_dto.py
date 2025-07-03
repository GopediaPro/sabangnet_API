from pydantic import BaseModel, Field
from typing import List, Optional


class DbToXmlByGubunRequest(BaseModel):
    """gubun별 DB to XML 변환 요청 DTO"""
    gubun: str = Field(..., description="몰구분 (마스터, 전문몰, 1+1)")


class DbToXmlByIdsRequest(BaseModel):
    """ID 리스트별 DB to XML 변환 요청 DTO"""
    ids: List[int] = Field(..., description="변환할 상품 ID 리스트", min_items=1)


class DbToXmlByProductNmRequest(BaseModel):
    """상품명별 DB to XML 변환 요청 DTO"""
    product_nm: str = Field(..., description="상품명 (부분 검색)", min_length=1)


class DbToXmlPaginationRequest(BaseModel):
    """페이징별 DB to XML 변환 요청 DTO"""
    skip: int = Field(default=0, description="건너뛸 개수", ge=0)
    limit: int = Field(default=10, description="조회할 개수", ge=1, le=1000)


class DbToXmlResponse(BaseModel):
    """DB to XML 변환 응답 DTO"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    xml_file_path: Optional[str] = Field(None, description="생성된 XML 파일 경로")
    processed_count: Optional[int] = Field(None, description="처리된 상품 개수")


class ProductRawDataCountResponse(BaseModel):
    """상품 데이터 개수 응답 DTO"""
    total_count: int = Field(..., description="총 상품 개수") 