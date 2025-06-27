from core.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.inspection import inspect

from models.product.product_raw_data import ProductRawData
from models.product.modified_product_data import ModifiedProductData


class ProductRepository:
    def __init__(self, session: AsyncSession = None):
        self.session = session

    def to_dict(self, obj) -> dict:
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

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
            .outerjoin(ModifiedProductData, ProductRawData.id == ModifiedProductData.product_raw_data_id)
            .where(ModifiedProductData.product_raw_data_id == None)
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
            .distinct(ModifiedProductData.product_raw_data_id)
            .order_by(ModifiedProductData.product_raw_data_id, ModifiedProductData.rev.desc())
        )
        result = await self.session.execute(query)
        raw_data: list[dict] = [row.__dict__ for row in result.scalars().all()]
        return raw_data


    async def find_product_raw_data_by_company_goods_cd(self, company_goods_cd: str) -> ProductRawData:
        query = select(ProductRawData).where(ProductRawData.compayny_goods_cd == company_goods_cd).limit(1)
        product_raw_data = await self.session.execute(query)
        return product_raw_data.scalar_one_or_none()
    

    async def find_modified_product_data_by_product_raw_data_id(self, product_raw_data_id: int) -> ModifiedProductData:
        query = select(ModifiedProductData).\
            where(ModifiedProductData.test_product_raw_data_id == product_raw_data_id).order_by(ModifiedProductData.rev.desc()).limit(1)
        modified_product_data = await self.session.execute(query)
        return modified_product_data.scalar_one_or_none()
        
    
    async def save_modified_product_name(self, product_raw_data: ProductRawData, rev: int, product_name: str) -> ModifiedProductData:

        query = insert(ModifiedProductData).values(
            test_product_raw_data_id=product_raw_data.id,
            goods_nm=product_name,
            goods_keyword=product_raw_data.goods_keyword,
            model_nm=product_raw_data.model_nm,
            model_no=product_raw_data.model_no,
            brand_nm=product_raw_data.brand_nm,
            compayny_goods_cd=product_raw_data.compayny_goods_cd,
            goods_search=product_raw_data.goods_search,
            goods_gubun=product_raw_data.goods_gubun,
            class_cd1=product_raw_data.class_cd1,
            class_cd2=product_raw_data.class_cd2,
            class_cd3=product_raw_data.class_cd3,
            class_cd4=product_raw_data.class_cd4,
            mall_gubun=product_raw_data.mall_gubun,
            partner_id=product_raw_data.partner_id,
            dpartner_id=product_raw_data.dpartner_id,
            maker=product_raw_data.maker,
            origin=product_raw_data.origin,
            make_year=product_raw_data.make_year,
            make_dm=product_raw_data.make_dm,
            goods_season=product_raw_data.goods_season,
            sex=product_raw_data.sex,
            status=product_raw_data.status,
            deliv_able_region=product_raw_data.deliv_able_region,
            tax_yn=product_raw_data.tax_yn,
            delv_type=product_raw_data.delv_type,
            delv_cost=product_raw_data.delv_cost,
            banpum_area=product_raw_data.banpum_area,
            goods_cost=product_raw_data.goods_cost,
            goods_price=product_raw_data.goods_price,
            goods_consumer_price=product_raw_data.goods_consumer_price,
            goods_cost2=product_raw_data.goods_cost2,
            char_1_nm=product_raw_data.char_1_nm,
            char_1_val=product_raw_data.char_1_val,
            char_2_nm=product_raw_data.char_2_nm,
            char_2_val=product_raw_data.char_2_val,
            img_path=product_raw_data.img_path,
            img_mall_jpg=product_raw_data.img_mall_jpg,
            img_add_2=product_raw_data.img_add_2,
            img_add_3=product_raw_data.img_add_3,
            img_add_4=product_raw_data.img_add_4,
            img_add_5=product_raw_data.img_add_5,
            img_add_6=product_raw_data.img_add_6,
            img_add_7=product_raw_data.img_add_7,
            img_add_8=product_raw_data.img_add_8,
            img_add_9=product_raw_data.img_add_9,
            img_add_10=product_raw_data.img_add_10,
            img_add_11_list=product_raw_data.img_add_11_list,
            img_add_12=product_raw_data.img_add_12,
            img_add_13=product_raw_data.img_add_13,
            img_add_14=product_raw_data.img_add_14,
            img_add_15=product_raw_data.img_add_15,
            img_add_16=product_raw_data.img_add_16,
            img_add_17=product_raw_data.img_add_17,
            img_add_18=product_raw_data.img_add_18,
            img_add_19=product_raw_data.img_add_19,
            img_add_20=product_raw_data.img_add_20,
            img_add_21=product_raw_data.img_add_21,
            img_add_22=product_raw_data.img_add_22,
            cert_img=product_raw_data.cert_img,
            import_cert_img=product_raw_data.import_cert_img,
            goods_remarks=product_raw_data.goods_remarks,
            certno=product_raw_data.certno,
            avlst_dm=product_raw_data.avlst_dm,
            avled_dm=product_raw_data.avled_dm,
            issuedate=product_raw_data.issuedate,
            certdate=product_raw_data.certdate,
            cert_agency=product_raw_data.cert_agency,
            certfield=product_raw_data.certfield,
            material=product_raw_data.material,
            opt_type=product_raw_data.opt_type,
            prop1_cd=product_raw_data.prop1_cd,
            prop_val1=product_raw_data.prop_val1,
            prop_val2=product_raw_data.prop_val2,
            prop_val3=product_raw_data.prop_val3,
            prop_val4=product_raw_data.prop_val4,
            prop_val5=product_raw_data.prop_val5,
            prop_val6=product_raw_data.prop_val6,
            prop_val7=product_raw_data.prop_val7,
            prop_val8=product_raw_data.prop_val8,
            prop_val9=product_raw_data.prop_val9,
            prop_val10=product_raw_data.prop_val10,
            prop_val11=product_raw_data.prop_val11,
            prop_val12=product_raw_data.prop_val12,
            prop_val13=product_raw_data.prop_val13,
            prop_val14=product_raw_data.prop_val14,
            prop_val15=product_raw_data.prop_val15,
            prop_val16=product_raw_data.prop_val16,
            prop_val17=product_raw_data.prop_val17,
            prop_val18=product_raw_data.prop_val18,
            prop_val19=product_raw_data.prop_val19,
            prop_val20=product_raw_data.prop_val20,
            prop_val21=product_raw_data.prop_val21,
            prop_val22=product_raw_data.prop_val22,
            prop_val23=product_raw_data.prop_val23,
            prop_val24=product_raw_data.prop_val24,
            prop_val25=product_raw_data.prop_val25,
            prop_val26=product_raw_data.prop_val26,
            prop_val27=product_raw_data.prop_val27,
            prop_val28=product_raw_data.prop_val28,
            prop_val29=product_raw_data.prop_val29,
            prop_val30=product_raw_data.prop_val30,
            prop_val31=product_raw_data.prop_val31,
            prop_val32=product_raw_data.prop_val32,
            prop_val33=product_raw_data.prop_val33,
            pack_code_str=product_raw_data.pack_code_str,
            goods_nm_en=product_raw_data.goods_nm_en,
            goods_remarks2=product_raw_data.goods_remarks2,
            goods_remarks3=product_raw_data.goods_remarks3,
            goods_remarks4=product_raw_data.goods_remarks4,
            importno=product_raw_data.importno,
            origin2=product_raw_data.origin2,
            expire_dm=product_raw_data.expire_dm,
            supply_save_yn=product_raw_data.supply_save_yn,
            descrition=product_raw_data.descrition,
            goods_nm_pr=product_raw_data.goods_nm_pr,
            stock_use_yn=product_raw_data.stock_use_yn,
            rev=rev+1).returning(ModifiedProductData)

        res = await self.session.execute(query)
        await self.session.commit()
        return res.scalar_one()