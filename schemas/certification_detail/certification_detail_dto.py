from pydantic import BaseModel

class CertificationDetailDto(BaseModel):
    id: int
    certification_field: str
    certification_code: str

    class Config:
        from_attributes = True