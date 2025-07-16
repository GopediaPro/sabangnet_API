from pydantic import BaseModel, Field


class ExcelRunMacroResponse(BaseModel):
    """
    엑셀 매크로 실행 및 업로드 응답 객체
    """
    success: bool = Field(..., description="성공 여부")
    template_code: str = Field(..., description="템플릿 코드")
    batch_id: int | None = Field(None, description="배치 ID")
    file_url: str | None = Field(None, description="업로드 파일 URL")
    object_name: str | None = Field(None, description="Minio 오브젝트명")
    message: str | None = Field(None, description="메시지 또는 에러")

    @classmethod
    def build_success(cls, template_code: str, batch_id: int, file_url: str, object_name: str):
        datetime_from_url = file_url.split("/")[-1].split("_")[0]
        return cls(
            success=True,
            template_code=template_code,
            batch_id=batch_id,
            file_url=file_url,
            object_name=object_name,
            message=datetime_from_url + " Success"
        )

    @classmethod
    def build_error(cls, template_code: str, batch_id: int, message: str):
        return cls(
            success=False,
            template_code=template_code,
            batch_id=batch_id,
            file_url=None,
            object_name=None,
            message=message
        )
