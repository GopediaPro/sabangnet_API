from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from services.product.product_read_service import ProductReadService
from services.product.product_create_db_to_excel_service import ProductDbExcelService


class ProductDbExcelUsecase:
    def __init__(self, product_read_service: ProductReadService):
        self.product_read_service = product_read_service

    async def convert_db_to_excel(self) -> StreamingResponse:
        return ProductDbExcelService.convert_db_to_excel(await self.product_read_service.get_product_raw_data_all())