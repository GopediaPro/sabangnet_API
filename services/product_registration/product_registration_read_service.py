from typing import Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from repository.product_registration_repository import ProductRegistrationRepository
from models.product.product_registration_data import ProductRegistrationRawData

class ProductRegistrationReadService:
    def __init__(self, session: AsyncSession):
        self.product_registration_repository = ProductRegistrationRepository(session)

    async def get_product_registration_by_product_nm(self, product_nm: str) -> ProductRegistrationRawData:
        return await self.product_registration_repository.find_product_registration_data_by_product_nm(product_nm)
    
    async def get_product_id_and_price_by_product_nm(self, product_nm: str) -> Tuple[int, Decimal]:
        return await self.product_registration_repository.find_product_id_and_price_by_product_nm(product_nm)