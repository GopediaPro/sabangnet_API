import logging
from pydantic import BaseModel, Field
from typing import List, Optional

logger = logging.getLogger(__name__)

logger.info("DbToXmlResponse 스키마 로드 시작...")


class DbToXmlResponse(BaseModel):
    """DB to XML 변환 응답 DTO"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    xml_file_path: Optional[str] = Field(None, description="생성된 XML 파일 경로")
    processed_count: Optional[int] = Field(None, description="처리된 상품 개수")


logger.info("DbToXmlResponse 스키마 정의 완료")
