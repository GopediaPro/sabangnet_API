from sqlalchemy.ext.asyncio import AsyncSession
from repository.product_repository import ProductRepository
from schemas.product.modified_product_dto import ModifiedProductDataDto


class ProductUpdateService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repository = ProductRepository(session)

    async def update_product_id_by_compayny_goods_cd(self, compayny_goods_cd: str, product_id: int):
        await self.product_repository.update_product_id_by_compayny_goods_cd(compayny_goods_cd, product_id)

    async def update_product_id_by_compayny_goods_cd_with_bracket_removal(self, response_compayny_goods_cd: str, product_id: int) -> bool:
        """
        DB에 저장된 compayny_goods_cd에서 '[', ']'를 제거한 후 
        response의 compayny_goods_cd와 매칭하여 product_id를 업데이트
        
        Args:
            response_compayny_goods_cd: response에서 받은 compayny_goods_cd
            product_id: 업데이트할 product_id
            
        Returns:
            bool: 업데이트 성공 여부
        """
        return await self.product_repository.update_product_id_by_compayny_goods_cd_with_bracket_removal(
            response_compayny_goods_cd, product_id
        )

    async def update_product_ids_by_compayny_goods_cd_with_bracket_removal_batch(self, compayny_goods_cd_and_product_ids: list[tuple[str, int]]) -> dict:
        """
        여러 개의 compayny_goods_cd와 product_id 쌍을 배치로 처리하여 업데이트
        
        Args:
            compayny_goods_cd_and_product_ids: (response_compayny_goods_cd, product_id) 튜플 리스트
            
        Returns:
            dict: 성공/실패 통계
        """
        return await self.product_repository.update_product_ids_by_compayny_goods_cd_with_bracket_removal_batch(
            compayny_goods_cd_and_product_ids
        )
