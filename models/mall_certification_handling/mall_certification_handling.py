from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base


class MallCertificationHandling(Base):
    __tablename__ = "mall_certification_handling"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_code: Mapped[str] = mapped_column(String(50))
    certification_detail_id: Mapped[int] = mapped_column(Integer, ForeignKey("certification_detail.id", name="certification_detail", ondelete="CASCADE"), nullable=False)
    before_certification_field: Mapped[str] = mapped_column(String(50))
    final_certification_field: Mapped[str] = mapped_column(String(50))
    
    @classmethod
    def builder(cls, shop_code: str, certification_detail_id: int, before_certification_field: str, final_certification_field: str):
        return cls(
            shop_code=shop_code,
            certification_detail_id=certification_detail_id,
            before_certification_field=before_certification_field,
            final_certification_field=final_certification_field
        )