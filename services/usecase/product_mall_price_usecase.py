from sqlalchemy.ext.asyncio import AsyncSession
from services.mall_price.mall_price_write_service import MallPriceWriteService
from services.product.product_read_service import ProductReadService
from schemas.mall_price.mall_price_dto import MallPriceDto
from utils.make_xml.mall_price_registration_xml import MallPriceRegistrationXml
from services.mall_price.mall_price_request_service import MallPriceRequestService
from utils.mall_price_response_parser import parse_sabangnet_response
from repository.count_executing_repository import CountExecutingRepository
from models.count_executing_data import CountExecuting
from file_server_handler import upload_to_file_server, get_file_server_url
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)

class ProductMallPriceUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.mall_price_write_service = MallPriceWriteService(session)
        self.product_read_service = ProductReadService(session)
        self.mall_price_registration_xml = MallPriceRegistrationXml()
        self.mall_price_request_service = MallPriceRequestService()

    async def setting_mall_price(self, compayny_goods_cd: str) -> MallPriceDto:
        product_raw_data_dto = await self.product_read_service.\
            get_product_by_compayny_goods_cd(compayny_goods_cd=compayny_goods_cd)
        
        mall_price_dto = await self.mall_price_write_service.\
            setting_mall_price(product_raw_data_id=product_raw_data_dto.id,
                               standard_price=product_raw_data_dto.goods_price,
                               product_nm=product_raw_data_dto.product_nm,
                               compayny_goods_cd=compayny_goods_cd)
        # db to xml (local save and send fileserver)
        count_repo = CountExecutingRepository(self.session)
        mall_price_create_db_count = await count_repo.get_and_increment(CountExecuting, "mall_price_create_db")
        xml_file_path = self.mall_price_registration_xml.make_mall_price_dto_registration_xml(
            mall_price_dto=mall_price_dto,
            count_rev=mall_price_create_db_count
        )
        # upload to file server
        object_name = upload_to_file_server(xml_file_path)
        logger.info(f"파일 서버에 업로드된 XML 파일 이름: {object_name}")
        xml_url = get_file_server_url(object_name)
        logger.info(f"파일 서버에 업로드된 XML URL: {xml_url}")
        # get xml url from fileserver and send to sabangnetAPI with request 
        response_text = self.mall_price_request_service.request_sabangnet_product_update(xml_url)
        success_items, failed_items = parse_sabangnet_response(response_text)
        processed_count = len(success_items) + len(failed_items)
        return {
            "success": True,
            "message": "상품정보 수정 요청 완료",
            "xml_file_path": xml_url,
            "processed_count": processed_count,
            "success_items": success_items,
            "failed_items": failed_items,
        }


    