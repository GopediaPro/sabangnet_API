from sqlalchemy.ext.asyncio import AsyncSession
from repository.product_registration_repository import ProductRegistrationRepository
from models.product.product_registration_data import ProductRegistrationRawData
from schemas.product_registration import ProductRegistrationDto


class ProductRegistrationReadService:
    def __init__(self, session: AsyncSession):
        self.product_registration_repository = ProductRegistrationRepository(session)
    
    async def get_products_all(self, skip: int = 0, limit: int = 100) -> list[ProductRegistrationDto]:
        products: list[ProductRegistrationRawData] = (
            await self
            .product_registration_repository
            .get_products_all(skip=skip, limit=limit)
        )
        return [ProductRegistrationDto.model_validate(product) for product in products]
    
    async def get_products_by_pagenation(self, page: int = 1, page_size: int = 20) -> list[ProductRegistrationDto]:
        products: list[ProductRegistrationRawData] = (
            await self
            .product_registration_repository
            .get_products_by_pagenation(
                page=page, page_size=page_size
            )
        )
        return [ProductRegistrationDto.model_validate(product) for product in products]
    