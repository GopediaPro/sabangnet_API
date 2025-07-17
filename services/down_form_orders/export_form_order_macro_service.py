from sqlalchemy.ext.asyncio import AsyncSession
from services.macro.order_macro_service import run_macro_with_db
from repository.export_form_order_repository import ExportFormOrderRepository

class ExportFormOrderMacroService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.export_form_order_repository = ExportFormOrderRepository(session)

    async def run_macro_with_db(self, template_code: str) -> int:
        return await run_macro_with_db(self.session, template_code)
