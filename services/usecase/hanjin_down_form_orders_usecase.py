import random
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from schemas.hanjin.hanjin_printWbls_dto import AddressItem
from schemas.hanjin.hanjin_printWbls_dto import PrintWblsRequest
from models.hanjin.hanjin_printwbls import HanjinPrintwbls
from models.down_form_orders.down_form_order import BaseDownFormOrder
from services.hanjin.adapter.hanjin_wbls_adapter import HanjinWblsAdapter
from services.hanjin.hanjin_print_read_service import HanjinPrintReadService
from services.hanjin.hanjin_print_create_service import HanjinPrintCreateService
from services.hanjin.hanjin_print_update_service import HanjinPrintUpdateService
from schemas.down_form_orders.down_form_order_dto import DownFormOrdersInvoiceNoUpdateDto
from services.down_form_orders.down_form_order_read_service import DownFormOrderReadService
from services.down_form_orders.down_form_order_update_service import DownFormOrderUpdateService
from utils.exceptions.down_form_orders_exceptions import DownFormOrderReadServiceException
from utils.exceptions.hanjin_wbls_exceptions import HanjinPrintCreateServiceException, HanjinPrintReadServiceException


logger = get_logger(__name__)


class HanjinDownFormOrdersUsecase(HanjinWblsAdapter):
    def __init__(self, session: AsyncSession = None):
        super().__init__()
        self.print_read_service = HanjinPrintReadService(session)
        self.print_create_service = HanjinPrintCreateService(session)
        self.print_update_service = HanjinPrintUpdateService(session)
        self.down_form_order_read_service = DownFormOrderReadService(session)
        self.down_form_order_update_service = DownFormOrderUpdateService(session)

    async def insert_invoice_no_to_down_form_orders(self, limit: int = 100) -> list[BaseDownFormOrder]:
        # invoice_no가 없는 주문 데이터 조회
        orders_without_invoice: list[BaseDownFormOrder] = await self.down_form_order_read_service.get_orders_without_invoice_no(limit)
        
        if not orders_without_invoice:
            raise DownFormOrderReadServiceException("invoice_no가 없는 주문 데이터가 없습니다.")
        
        ##################################################################################################

        # hanjin_printwbls 테이블에 기초 데이터 입력
        wbls_list: list[HanjinPrintwbls] = await self.print_create_service.create_printwbls_from_down_form_orders(orders_without_invoice)
        
        if not wbls_list:
            raise HanjinPrintCreateServiceException("생성된 hanjin_printwbls 레코드가 없습니다.")
        
        logger.info(f"down_form_orders에서 {len(wbls_list)}건의 hanjin_printwbls 레코드 생성 완료")

        ##################################################################################################
        
        # 기초 레코드 조회
        base_records = await self.print_read_service.get_hanjin_printwbls_for_api_request(limit)
        
        if not base_records:
            raise HanjinPrintReadServiceException("API 요청을 위한 기초 레코드가 없습니다.")
        
        ##################################################################################################
        
        # 현재 날짜로 YYMMDD 형식 생성
        current_date = datetime.now().strftime("%y%m%d")
        
        # API 요청 데이터 준비
        address_item_list = []
        for i, base_record in enumerate(base_records, 1):
            # msg_key 생성: YYMMDD + random num(XX) + 요청개수순서(1,2,3,4,5,...)
            random_num = random.randint(10, 99)
            msg_key = f"{current_date}{random_num:02d}{i:02d}"
            
            address_item = AddressItem(
                csr_num=self.get_hanjin_csr_num(),
                address=base_record.prt_add,
                snd_zip=base_record.snd_zip,
                rcv_zip=base_record.zip_cod,
                msg_key=msg_key
            )
            address_item_list.append(address_item)
        
        # PrintWblsRequest 객체 생성
        print_request = PrintWblsRequest(
            address_list=address_item_list
        )
        
        # 한진 API 호출
        api_response = await self.generate_print_wbls_with_env_vars_from_api(print_request)
        
        ##################################################################################################
        
        # 응답 데이터로 레코드 업데이트
        updated_records: list[HanjinPrintwbls] = []
        if api_response.address_list:
            for i, address_result in enumerate(api_response.address_list):
                if i < len(base_records):
                    record = base_records[i]
                    # API 응답 데이터를 딕셔너리로 변환
                    response_data = address_result.model_dump()
                    # 레코드 업데이트
                    updated_record = await self.print_update_service.update_with_api_response(record.id, response_data)
                    updated_records.append(updated_record)
        
        logger.info(f"hanjin_printwbls {len(updated_records)}건 API 처리 및 업데이트 완료")

        ##################################################################################################

        idx_invoice_no_dict_list: list[dict[str, str]] = [
            {
                "idx": record.idx,
                "invoice_no": record.wbl_num
            } for record in updated_records
        ]
        
        results: list[DownFormOrdersInvoiceNoUpdateDto] = (
            await self
            .down_form_order_update_service
            .bulk_update_down_form_order_invoice_no_by_idx(idx_invoice_no_dict_list)
        )

        logger.info(f"down_form_orders {len(results)}건의 invoice_no 업데이트 완료")

        return results