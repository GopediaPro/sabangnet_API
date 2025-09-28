from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from models.mall_price.product_mall_value import ProductMallValue
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class ProductMallValueRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_gubun_and_company_goods_cd(self, gubun: str, compayny_goods_cd: str) -> ProductMallValue:
        """gubun과 compayny_goods_cd로 기존 데이터 조회"""
        try:
            query = select(ProductMallValue).where(
                and_(
                    ProductMallValue.gubun == gubun,
                    ProductMallValue.compayny_goods_cd == compayny_goods_cd
                )
            ).limit(1)
            
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"ProductMallValue 조회 중 오류: {e}")
            raise

    async def save_product_mall_value(self, product_mall_value: ProductMallValue) -> ProductMallValue:
        """새로운 ProductMallValue 저장"""
        try:
            self.session.add(product_mall_value)
            await self.session.commit()
            await self.session.refresh(product_mall_value)
            logger.info(f"ProductMallValue 생성 완료: {product_mall_value.compayny_goods_cd}")
            return product_mall_value
        except Exception as e:
            await self.session.rollback()
            logger.error(f"ProductMallValue 저장 중 오류: {e}")
            raise

    async def update_product_mall_value(self, existing_id: int, new_obj: ProductMallValue) -> ProductMallValue:
        """기존 ProductMallValue 업데이트"""
        try:
            # 기존 객체 조회
            existing_obj = await self.session.get(ProductMallValue, existing_id)
            if not existing_obj:
                raise ValueError(f"ProductMallValue with id {existing_id} not found")
            
            # 기존 객체의 필드들을 새 객체의 값으로 업데이트
            for key, value in new_obj.__dict__.items():
                if not key.startswith('_') and key != 'id':  # private 속성과 id 제외
                    setattr(existing_obj, key, value)
            
            await self.session.commit()
            await self.session.refresh(existing_obj)
            logger.info(f"ProductMallValue 업데이트 완료: {existing_obj.compayny_goods_cd}")
            return existing_obj
        except Exception as e:
            await self.session.rollback()
            logger.error(f"ProductMallValue 업데이트 중 오류: {e}")
            raise

    async def upsert_product_mall_value(self, product_mall_value: ProductMallValue) -> ProductMallValue:
        """gubun과 compayny_goods_cd 기준으로 upsert"""
        try:
            # 기존 데이터 조회
            existing = await self.find_by_gubun_and_company_goods_cd(
                gubun=product_mall_value.gubun,
                compayny_goods_cd=product_mall_value.compayny_goods_cd
            )
            
            if existing:
                # 업데이트
                logger.info(f"기존 데이터 발견, 업데이트 수행: {product_mall_value.compayny_goods_cd}")
                return await self.update_product_mall_value(existing.id, product_mall_value)
            else:
                # 생성
                logger.info(f"새 데이터 생성: {product_mall_value.compayny_goods_cd}")
                return await self.save_product_mall_value(product_mall_value)
                
        except Exception as e:
            logger.error(f"ProductMallValue upsert 중 오류: {e}")
            raise
