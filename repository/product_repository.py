from typing import Optional, List
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, func
from models.product.product_raw_data import ProductRawData
from models.product.modified_product_data import ModifiedProductData
from utils.logs.sabangnet_logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


class ProductRepository:
    def __init__(self, session: AsyncSession = None):
        self.session = session

    def to_dict(self, obj) -> dict:
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
    
    async def find_product_raw_data_by_product_nm_and_gubun(self, product_nm: str, gubun: str) -> ProductRawData:
        query = select(ProductRawData).where(ProductRawData.product_nm == product_nm, ProductRawData.gubun == gubun)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_products_all(self, skip: int, limit: int) -> list[ProductRawData]:
        query = (
            select(ProductRawData)
            .offset(skip)
            .limit(limit)
            .order_by(ProductRawData.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_products_by_pagenation(self, page: int, page_size: int) -> list[ProductRawData]:
        query = (
            select(ProductRawData)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .order_by(ProductRawData.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def product_raw_data_create(self, product_data: list[dict]) -> list[int]:
        """
        Insert data to database and return id list.
        """
        try:
            query = insert(ProductRawData).returning(ProductRawData.id)
            result = await self.session.execute(query, product_data)
            await self.session.commit()
            return [row[0] for row in result.fetchall()]
        except IntegrityError as e:
            await self.session.rollback()
            print(f"[IntegrityError] {e}")
            raise
        except Exception as e:
            await self.session.rollback()
            print(f"[Unknown Error] {e}")
            raise
        finally:
            await self.session.close()

    async def product_get_next_rev(self, product_raw_id: int) -> int:
        """
        Get next rev.
        """
        query = select(func.max(ModifiedProductData.rev)).where(
            ModifiedProductData.test_product_raw_data_id == product_raw_id)
        result = await self.session.execute(query)
        max_rev = result.scalar_one_or_none()

        return (max_rev or 0) + 1
    
    async def prop1_cd_update(self, prop1_cd: int) -> str:
        """
        Update prop1_cd value.
        """
        prop1_cd = f"{int(prop1_cd):03}"
        if len(prop1_cd) != 3:
            raise ValueError("prop1_cd는 1~3자리 숫자여야 합니다.")
        return prop1_cd
    
    async def get_product_raw_data(self, product_raw_id: int) -> dict:
        """
        Get product raw data.
        """
        result = await self.session.execute(
            select(ProductRawData).where(
                ProductRawData.id == int(product_raw_id))
        )
        raw_data = result.scalar_one_or_none()
        if raw_data is None:
            raise ValueError(f"ID {product_raw_id}에 해당하는 상품을 찾을 수 없습니다.")
        return raw_data

    async def get_product_raw_data_all(self) -> list[ProductRawData]:
        """
        test_product_raw_data 테이블의 모든 데이터 조회
        Returns:
            ProductRawData 리스트
        """
        query = select(ProductRawData).order_by(ProductRawData.id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_product_raw_data(self) -> int:
        """
        test_product_raw_data 테이블 총 개수 조회
        Returns:
            총 개수
        """
        query = select(func.count(ProductRawData.id))
        result = await self.session.execute(query)
        return result.scalar()

    async def insert_product_ids(self, product_ids: list[int]):
        """
        product_id 리스트를 DB에 저장
        (예시: ProductRegistrationRawData 테이블에 product_id만 저장)
        """
        for pid in product_ids:
            obj = ProductRawData(product_id=pid)
            self.session.add(obj)
        await self.session.commit()

    async def modified_product_data_create(self, new_raw_dict: dict, returning) -> dict:
        query = insert(ModifiedProductData).returning(returning)
        result = await self.session.execute(query, new_raw_dict)
        await self.session.commit()

        modified_data = result.scalar_one_or_none()
        return modified_data

    async def prodout_prop1_cd_update(self, product_raw_id: int, prop1_cd: int) -> dict:
        """
        Update prop1_cd value.
        """
        # 빈값인 경우 기본값 사용
        prop1_cd = await self.prop1_cd_update(prop1_cd)

        # 1. raw 데이터 조회
        raw_data = await self.get_product_raw_data(product_raw_id)
        
        # 2. 다음 rev 조회
        next_rev = await self.product_get_next_rev(raw_data.id)

        # 3. 속성값 제거
        new_raw_dict = raw_data.__dict__.copy()
        new_raw_dict.pop('_sa_instance_state')
        new_raw_dict.pop('id')
        new_raw_dict.pop('created_at')
        new_raw_dict.pop('updated_at')

        # 4. 속성값 변경
        print(f"변경전 prop1_cd: {new_raw_dict['prop1_cd']}")
        new_raw_dict["prop1_cd"] = prop1_cd
        new_raw_dict['test_product_raw_data_id'] = raw_data.id  # 외래키 설정
        new_raw_dict['rev'] = next_rev  # 다음 rev 설정
        print(f"변경후 prop1_cd: {new_raw_dict['prop1_cd']}")
        print(new_raw_dict)

        # 5. ModifiedProductData에 insert
        modified_data = await self.modified_product_data_create(new_raw_dict, ModifiedProductData)
        modified_dict = self.to_dict(modified_data)
        return modified_dict

    async def get_unmodified_raws(self) -> list[dict]:
        """
        Get unmodified product data.
        """
        query = (
            select(ProductRawData)
            .outerjoin(ModifiedProductData, ProductRawData.id == ModifiedProductData.test_product_raw_data_id)
            .where(ModifiedProductData.test_product_raw_data_id == None)
        )
        result = await self.session.execute(query)
        raw_data: list[dict] = [row.__dict__ for row in result.scalars().all()]
        return raw_data

    async def get_modified_raws(self) -> list[dict]:
        """
        Get modified product data.
        """
        query = (
            select(ModifiedProductData)
            .distinct(ModifiedProductData.test_product_raw_data_id)
            .order_by(ModifiedProductData.test_product_raw_data_id, ModifiedProductData.rev.desc())
        )
        result = await self.session.execute(query)
        raw_data: list[dict] = [row.__dict__ for row in result.scalars().all()]
        return raw_data

    async def find_product_raw_data_by_company_goods_cd(self, company_goods_cd: str) -> ProductRawData:
        query = select(ProductRawData).where(ProductRawData.compayny_goods_cd == company_goods_cd)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_product_raw_data_by_company_goods_cds(self, company_goods_cds: List[str]) -> List[ProductRawData]:
        """
        특정 company_goods_cd 목록으로 product_raw_data 조회
        Args:
            company_goods_cds: 조회할 company_goods_cd 목록
        Returns:
            ProductRawData 목록
        """
        if not company_goods_cds:
            return []
        
        query = select(ProductRawData).where(ProductRawData.compayny_goods_cd.in_(company_goods_cds))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_product_raw_data_by_company_goods_cd(self, company_goods_cd: str, update_data: dict) -> bool:
        """
        company_goods_cd로 product_raw_data를 update
        Args:
            company_goods_cd: 업데이트할 상품의 company_goods_cd
            update_data: 업데이트할 데이터 딕셔너리
        Returns:
            업데이트 성공 여부
        """
        try:
            query = update(ProductRawData).where(ProductRawData.compayny_goods_cd == company_goods_cd).values(**update_data)
            result = await self.session.execute(query)
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            print(f"[Update Error] {e}")
            raise
        finally:
            await self.session.close()

    async def upsert_product_raw_data(self, product_data: dict) -> dict:
        """
        company_goods_cd가 있으면 update, 없으면 create
        Args:
            product_data: 상품 데이터 딕셔너리
        Returns:
            {'success': bool, 'action': str, 'company_goods_cd': str}
        """
        company_goods_cd = product_data.get('compayny_goods_cd')
        if not company_goods_cd:
            raise ValueError("company_goods_cd가 필요합니다.")
        
        # 기존 데이터 조회
        existing_data = await self.find_product_raw_data_by_company_goods_cd(company_goods_cd)
        
        if existing_data:
            # 기존 데이터가 있으면 update
            logger.info(f"기존 데이터 발견, update 수행: {company_goods_cd}")
            success = await self.update_product_raw_data_by_company_goods_cd(company_goods_cd, product_data)
            return {
                'success': success,
                'action': 'updated',
                'company_goods_cd': company_goods_cd
            }
        else:
            # 기존 데이터가 없으면 create
            logger.info(f"새 데이터 생성: {company_goods_cd}")
            try:
                query = insert(ProductRawData).returning(ProductRawData.id)
                result = await self.session.execute(query, [product_data])
                await self.session.commit()
                return {
                    'success': True,
                    'action': 'created',
                    'company_goods_cd': company_goods_cd
                }
            except Exception as e:
                await self.session.rollback()
                logger.error(f"[Insert Error] {e}")
                raise
            finally:
                await self.session.close()

    async def find_product_id_raw_data_by_product_nm_and_gubun(self, product_nm: str, gubun: str) -> Optional[int]:
        """상품명과 구분으로 test_product_raw_data의 ID 조회"""
        # SELECT id FROM test_product_raw_data WHERE product_nm = ? AND gubun = ?
        query = select(ProductRawData.id).where(
            ProductRawData.product_nm == product_nm,
            ProductRawData.gubun == gubun
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def find_modified_product_data_by_product_raw_data_id(self, product_raw_data_id: int) -> ModifiedProductData:
        query = select(ModifiedProductData).\
            where(ModifiedProductData.test_product_raw_data_id == product_raw_data_id).order_by(ModifiedProductData.rev.desc()).limit(1)
        modified_product_data = await self.session.execute(query)
        return modified_product_data.scalar_one_or_none()

    async def save_modified_product_name(self, product_raw_data: ProductRawData, rev: int, product_name: str) -> ModifiedProductData:
        # 1. Get all column names from the model
        columns = [c.key for c in inspect(ModifiedProductData).mapper.column_attrs
                   if c.key != 'id']
        
        # 2. Build the insert dict
        insert_dict = {}
        for col in columns:
            if col == "goods_nm":
                insert_dict[col] = product_name
            elif col == "rev":
                insert_dict[col] = rev
            elif col == "test_product_raw_data_id":
                insert_dict[col] = product_raw_data.id
            else:
                # Try to get the value from product_raw_data, fallback to None
                insert_dict[col] = getattr(product_raw_data, col, None)
        
        # 3. Insert using the dict
        query = insert(ModifiedProductData).values(**insert_dict).returning(ModifiedProductData)
        res = await self.session.execute(query)
        await self.session.commit()
        return res.scalar_one()

    async def get_product_raw_data_all(self) -> list[ProductRawData]:
        """
        test_product_raw_data 테이블의 모든 데이터 조회
        Returns:
            ProductRawData 리스트
        """
        query = select(ProductRawData).order_by(ProductRawData.id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_product_raw_data_by_gubun(self, gubun: str) -> list[ProductRawData]:
        """
        gubun 조건으로 test_product_raw_data 테이블 데이터 조회
        Args:
            gubun: 몰구분 (마스터, 전문몰, 1+1)
        Returns:
            ProductRawData 리스트
        """
        query = select(ProductRawData).where(ProductRawData.gubun == gubun).order_by(ProductRawData.id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_product_raw_data_by_ids(self, ids: list[int]) -> list[ProductRawData]:
        """
        ID 리스트로 test_product_raw_data 테이블 데이터 조회
        Args:
            ids: 조회할 ID 리스트
        Returns:
            ProductRawData 리스트
        """
        query = select(ProductRawData).where(ProductRawData.id.in_(ids)).order_by(ProductRawData.id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_product_raw_data_by_product_nm(self, product_nm: str) -> list[ProductRawData]:
        """
        상품명으로 test_product_raw_data 테이블 데이터 조회
        Args:
            product_nm: 상품명
        Returns:
            ProductRawData 리스트
        """
        query = select(ProductRawData).where(ProductRawData.product_nm.like(f"%{product_nm}%")).order_by(ProductRawData.id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_product_raw_data_pagination(self, skip: int = 0, limit: int = 10) -> list[ProductRawData]:
        """
        test_product_raw_data 테이블 데이터 페이징 조회
        Args:
            skip: 건너뛸 개수
            limit: 조회할 개수
        Returns:
            ProductRawData 리스트
        """
        query = select(ProductRawData).offset(skip).limit(limit).order_by(ProductRawData.id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_product_id_by_compayny_goods_cd(self, compayny_goods_cd: str, product_id: int) -> None:
        """
        compayny_goods_cd가 일치하는 ProductRawData의 product_id를 업데이트
        """
        query = (
            update(ProductRawData)
            .where(ProductRawData.compayny_goods_cd == compayny_goods_cd)
            .values(product_id=product_id)
        )
        await self.session.execute(query)
        await self.session.commit()

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
        # DB에서 모든 ProductRawData 조회
        query = select(ProductRawData)
        result = await self.session.execute(query)
        all_products = result.scalars().all()
        
        # DB의 compayny_goods_cd에서 '[', ']' 제거 후 매칭
        for product in all_products:
            db_compayny_goods_cd_cleaned = product.compayny_goods_cd.replace('[', '').replace(']', '')
            
            if db_compayny_goods_cd_cleaned == response_compayny_goods_cd:
                # 매칭되는 경우 product_id 업데이트
                update_query = (
                    update(ProductRawData)
                    .where(ProductRawData.id == product.id)
                    .values(product_id=product_id)
                )
                await self.session.execute(update_query)
                await self.session.commit()
                return True
        
        return False

    async def update_product_ids_by_compayny_goods_cd_with_bracket_removal_batch(self, compayny_goods_cd_and_product_ids: list[tuple[str, int]]) -> dict:
        """
        여러 개의 compayny_goods_cd와 product_id 쌍을 배치로 처리하여 업데이트
        
        Args:
            compayny_goods_cd_and_product_ids: (response_compayny_goods_cd, product_id) 튜플 리스트
            
        Returns:
            dict: 성공/실패 통계
        """
        # DB에서 모든 ProductRawData를 한 번만 조회
        query = select(ProductRawData)
        result = await self.session.execute(query)
        all_products = result.scalars().all()
        
        # DB 데이터를 딕셔너리로 변환 (성능 최적화)
        db_products_dict = {}
        for product in all_products:
            db_compayny_goods_cd_cleaned = product.compayny_goods_cd.replace('[', '').replace(']', '')
            db_products_dict[db_compayny_goods_cd_cleaned] = product.id
        
        success_count = 0
        failed_count = 0
        failed_items = []
        
        # 각 response compayny_goods_cd에 대해 매칭 시도
        for response_compayny_goods_cd, product_id in compayny_goods_cd_and_product_ids:
            if response_compayny_goods_cd in db_products_dict:
                # 매칭되는 경우 product_id 업데이트
                update_query = (
                    update(ProductRawData)
                    .where(ProductRawData.id == db_products_dict[response_compayny_goods_cd])
                    .values(product_id=product_id)
                )
                await self.session.execute(update_query)
                success_count += 1
            else:
                failed_count += 1
                failed_items.append({
                    'response_compayny_goods_cd': response_compayny_goods_cd,
                    'product_id': product_id
                })
        
        # 모든 업데이트를 한 번에 커밋
        await self.session.commit()
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_items': failed_items
        }
        
    async def fetch_test_product_raw_data_for_excel(
            self,
            sort_order: Optional[str] = None,
            created_before: Optional[datetime] = None
        ) -> List[ProductRawData]:
            """
            test_product_raw_data 테이블 데이터 조회 (Excel 다운로드용)
            """
            try:
                stmt = select(ProductRawData)

                if created_before:
                    stmt = stmt.where(ProductRawData.created_at <= created_before)

                if sort_order == "asc":
                    stmt = stmt.order_by(ProductRawData.created_at.asc())
                elif sort_order == "desc":
                    stmt = stmt.order_by(ProductRawData.created_at.desc())
                else:
                    stmt = stmt.order_by(ProductRawData.id.asc())

                result = await self.session.execute(stmt)
                return result.scalars().all()

            except Exception as e:
                logger.error(f"[fetch_product_raw_data_for_excel] 실패: {e}")
                raise

async def insert_product_raw_data(session: AsyncSession, data: dict) -> ProductRawData:
    obj = ProductRawData(**data)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj