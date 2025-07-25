from models.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String


class MacroInfo(Base):
    """
    매크로 정보 테이블(macro_info)의 ORM 매핑 모델
    """

    __tablename__ = "macro_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    form_name: Mapped[str] = mapped_column(String(50))
    macro_name: Mapped[str] = mapped_column(String(50))