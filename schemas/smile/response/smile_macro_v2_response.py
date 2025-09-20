from typing import Optional
from pydantic import BaseModel, Field

class SmileMacroV2Response(BaseModel):
    batch_id: int = Field(..., description="배치 프로세스 ID")
    processed_count: int = Field(..., description="처리된 건수")
    a_file_url: Optional[str] = Field(None, description="A 파일 URL (옥션)")
    g_file_url: Optional[str] = Field(None, description="G 파일 URL (G마켓)")
    full_file_url: Optional[str] = Field(None, description="전체 파일 URL")
    bundle_url: Optional[str] = Field(None, description="번들 파일 URL")
    message: str = Field(..., description="처리 결과 메시지")
    
    class Config:
        from_attributes = True
