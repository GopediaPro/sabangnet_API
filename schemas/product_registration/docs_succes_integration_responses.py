# schemas/docs_responses.py
from typing import Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from schemas.integration_response import Metadata

T = TypeVar("T")

class SuccessResponseSchema(GenericModel, Generic[T]):
    """Swagger 문서화 전용 성공 응답 스키마"""
    success: bool = Field(..., description="성공 여부", example=True)
    data: T = Field(..., description="데이터")  # ✅ 어떤 DTO든 올 수 있음
    metadata: Metadata = Field(..., description="메타데이터")
