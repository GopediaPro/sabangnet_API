"""
Product Mycategory DTO 클래스들
Excel 데이터와 API 응답을 위한 데이터 전송 객체
"""

from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ProductMycategoryCreateDto(BaseModel):
    """상품 카테고리 데이터 생성용 DTO"""
    
    class_cd1: Optional[str] = Field(None, max_length=50, description="대분류_분류코드")
    class_nm1: Optional[str] = Field(None, max_length=50, description="대분류_분류명")
    class_pr1: Optional[str] = Field(None, max_length=50, description="대분류_전시순서")
    class_cd2: Optional[str] = Field(None, max_length=50, description="중분류_분류코드")
    class_nm2: Optional[str] = Field(None, max_length=50, description="중분류_분류명")
    class_pr2: Optional[str] = Field(None, max_length=50, description="중분류_전시순서")
    class_cd3: Optional[str] = Field(None, max_length=50, description="소분류_분류코드")
    class_nm3: Optional[str] = Field(None, max_length=50, description="소분류_분류명")
    class_pr3: Optional[str] = Field(None, max_length=50, description="소분류_전시순서")
    class_cd4: Optional[str] = Field(None, max_length=50, description="세분류_분류코드")
    class_nm4: Optional[str] = Field(None, max_length=50, description="세분류_분류명")
    class_pr4: Optional[str] = Field(None, max_length=50, description="세분류_전시순서")

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }