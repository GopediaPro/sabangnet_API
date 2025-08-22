from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.hanjin.hanjin_printwbls import HanjinPrintwbls
from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.hanjin.hanjin_printWbls_dto import AddressResult
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class HanjinPrintwblsRepository:
    """한진택배 운송장 출력 Repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _create_hanjin_printwbls_from_dto(self, address_result: AddressResult, idx: Optional[str] = None) -> HanjinPrintwbls:
        """
        AddressResult DTO를 HanjinPrintwbls 모델로 변환합니다.
        
        Args:
            address_result: AddressResult 객체
            idx: 주문번호 (선택사항)
            
        Returns:
            HanjinPrintwbls 객체
        """
        record_data = address_result.model_dump()
        record_data['idx'] = idx
        return HanjinPrintwbls(**record_data)
    
    async def create_printwbls_record(self, address_result: AddressResult, idx: Optional[str] = None) -> HanjinPrintwbls:
        """
        운송장 출력 결과를 데이터베이스에 저장합니다.
        
        Args:
            address_result: AddressResult 객체
            idx: 주문번호 (선택사항)
            
        Returns:
            생성된 HanjinPrintwbls 객체
        """
        try:
            # AddressResult DTO를 HanjinPrintwbls 모델로 변환
            printwbls_record = self._create_hanjin_printwbls_from_dto(address_result, idx)
            
            self.session.add(printwbls_record)
            await self.session.commit()
            await self.session.refresh(printwbls_record)
            
            logger.info(f"운송장 출력 결과 저장 성공: msg_key={address_result.msg_key}, wbl_num={address_result.wbl_num}")
            return printwbls_record
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"운송장 출력 결과 저장 실패: {str(e)}")
            raise
        finally:
            await self.session.close()
    
    async def create_multiple_printwbls_records(
        self, 
        address_results: List[AddressResult], 
        idx: Optional[str] = None
    ) -> List[HanjinPrintwbls]:
        """
        여러 운송장 출력 결과를 데이터베이스에 저장합니다.
        
        Args:
            address_results: AddressResult 객체 리스트
            idx: 주문번호 (선택사항)
            
        Returns:
            생성된 HanjinPrintwbls 객체 리스트
        """
        try:
            # AddressResult DTO들을 HanjinPrintwbls 모델로 변환
            printwbls_records = [
                self._create_hanjin_printwbls_from_dto(address_result, idx)
                for address_result in address_results
            ]
            
            self.session.add_all(printwbls_records)
            await self.session.commit()
            
            # 각 레코드를 refresh
            for record in printwbls_records:
                await self.session.refresh(record)
            
            logger.info(f"운송장 출력 결과 {len(address_results)}건 저장 성공")
            return printwbls_records
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"운송장 출력 결과 일괄 저장 실패: {str(e)}")
            raise
        finally:
            await self.session.close()
    
    async def get_by_msg_key(self, msg_key: str) -> Optional[HanjinPrintwbls]:
        """
        msg_key로 운송장 출력 결과를 조회합니다.
        
        Args:
            msg_key: 메시지 키
            
        Returns:
            HanjinPrintwbls 객체 또는 None
        """
        try:
            query = select(HanjinPrintwbls).where(HanjinPrintwbls.msg_key == msg_key)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
    
    async def get_by_wbl_num(self, wbl_num: str) -> Optional[HanjinPrintwbls]:
        """
        운송장번호로 운송장 출력 결과를 조회합니다.
        
        Args:
            wbl_num: 운송장번호
            
        Returns:
            HanjinPrintwbls 객체 또는 None
        """
        try:
            query = select(HanjinPrintwbls).where(HanjinPrintwbls.wbl_num == wbl_num)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()
    
    async def get_by_idx(self, idx: str) -> List[HanjinPrintwbls]:
        """
        주문번호로 운송장 출력 결과들을 조회합니다.
        
        Args:
            idx: 주문번호
            
        Returns:
            HanjinPrintwbls 객체 리스트
        """
        try:
            query = select(HanjinPrintwbls).where(HanjinPrintwbls.idx == idx)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close() 

    async def create_printwbls_from_down_form_orders(self, down_form_orders: List[BaseDownFormOrder]) -> List[HanjinPrintwbls]:
        """
        down_form_orders 데이터를 기반으로 hanjin_printwbls 레코드를 생성합니다.
        
        Args:
            down_form_orders: down_form_orders 테이블의 데이터 리스트
            
        Returns:
            생성된 HanjinPrintwbls 객체 리스트
        """
        try:
            printwbls_records = []
            
            for order in down_form_orders:
                # idx, receive_addr, receive_zipcode를 매핑
                printwbls_record = HanjinPrintwbls(
                    idx=order.idx,
                    prt_add=order.receive_addr,
                    zip_cod=order.receive_zipcode,
                    # TODO: 임시 send_zip 값 추가. 추후 수정 필요. 
                    snd_zip="08609"
                )
                printwbls_records.append(printwbls_record)
            
            self.session.add_all(printwbls_records)
            await self.session.commit()
            
            # 각 레코드를 refresh
            for record in printwbls_records:
                await self.session.refresh(record)
            
            logger.info(f"down_form_orders에서 {len(printwbls_records)}건의 hanjin_printwbls 레코드 생성 성공")
            return printwbls_records
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"down_form_orders에서 hanjin_printwbls 생성 실패: {str(e)}")
            raise
        finally:
            await self.session.close()

    async def update_with_api_response(self, record_id: int, api_response: dict) -> HanjinPrintwbls:
        """
        API 응답으로 hanjin_printwbls 레코드를 업데이트합니다.
        
        Args:
            record_id: 업데이트할 레코드 ID
            api_response: API 응답 데이터
            
        Returns:
            업데이트된 HanjinPrintwbls 객체
        """
        try:
            # 레코드 조회
            record = await self.session.get(HanjinPrintwbls, record_id)
            if not record:
                raise ValueError(f"ID {record_id}에 해당하는 레코드를 찾을 수 없습니다.")
            
            # API 응답 데이터로 업데이트
            if 'msg_key' in api_response:
                record.msg_key = api_response['msg_key']
            if 'result_code' in api_response:
                record.result_code = api_response['result_code']
            if 'result_message' in api_response:
                record.result_message = api_response['result_message']
            if 's_tml_nam' in api_response:
                record.s_tml_nam = api_response['s_tml_nam']
            if 's_tml_cod' in api_response:
                record.s_tml_cod = api_response['s_tml_cod']
            if 'tml_nam' in api_response:
                record.tml_nam = api_response['tml_nam']
            if 'tml_cod' in api_response:
                record.tml_cod = api_response['tml_cod']
            if 'cen_nam' in api_response:
                record.cen_nam = api_response['cen_nam']
            if 'cen_cod' in api_response:
                record.cen_cod = api_response['cen_cod']
            if 'pd_tim' in api_response:
                record.pd_tim = api_response['pd_tim']
            if 'dom_rgn' in api_response:
                record.dom_rgn = api_response['dom_rgn']
            if 'hub_cod' in api_response:
                record.hub_cod = api_response['hub_cod']
            if 'dom_mid' in api_response:
                record.dom_mid = api_response['dom_mid']
            if 'es_cod' in api_response:
                record.es_cod = api_response['es_cod']
            if 'grp_rnk' in api_response:
                record.grp_rnk = api_response['grp_rnk']
            if 'es_nam' in api_response:
                record.es_nam = api_response['es_nam']
            if 'wbl_num' in api_response:
                record.wbl_num = api_response['wbl_num']
            
            await self.session.commit()
            await self.session.refresh(record)
            
            logger.info(f"hanjin_printwbls 레코드 업데이트 성공: ID={record_id}, msg_key={record.msg_key}")
            return record
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"hanjin_printwbls 레코드 업데이트 실패: {str(e)}")
            raise
        finally:
            await self.session.close()
        
    async def get_hanjin_printwbls_for_api_request(self, limit: int = 100) -> List[HanjinPrintwbls]:
        """
        API 요청을 위해 필요한 데이터가 있는 hanjin_printwbls 레코드들을 조회합니다.
        
        Args:
            limit: 조회할 최대 건수
            
        Returns:
            HanjinPrintwbls 객체 리스트
        """
        try:
            query = select(HanjinPrintwbls).where(
                (HanjinPrintwbls.prt_add != None) & 
                (HanjinPrintwbls.prt_add != '') &
                (HanjinPrintwbls.snd_zip != None) &
                (HanjinPrintwbls.snd_zip != '') &
                (HanjinPrintwbls.zip_cod != None) &
                (HanjinPrintwbls.zip_cod != '')
            ).order_by(HanjinPrintwbls.id.desc()).limit(limit)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"API 요청용 레코드 조회 실패: {str(e)}")
            raise
        finally:
            await self.session.close()

    async def create_from_api_response(
        self, 
        idx: str, 
        prt_add: str, 
        zip_cod: str, 
        snd_zip: str, 
        api_response_data: dict
    ) -> HanjinPrintwbls:
        """
        API 응답 데이터를 기반으로 새로운 hanjin_printwbls 레코드를 생성합니다.
        
        Args:
            idx: 주문번호
            prt_add: 배송지 주소
            zip_cod: 배송지 우편번호
            snd_zip: 출발지 우편번호
            api_response_data: API 응답 데이터
            
        Returns:
            생성된 HanjinPrintwbls 객체
        """
        try:
            # 기본 데이터 설정
            record_data = {
                'idx': idx,
                'prt_add': prt_add,
                'zip_cod': zip_cod,
                'snd_zip': snd_zip,
            }
            
            # API 응답 데이터 추가
            if 'msg_key' in api_response_data:
                record_data['msg_key'] = api_response_data['msg_key']
            if 'result_code' in api_response_data:
                record_data['result_code'] = api_response_data['result_code']
            if 'result_message' in api_response_data:
                record_data['result_message'] = api_response_data['result_message']
            if 's_tml_nam' in api_response_data:
                record_data['s_tml_nam'] = api_response_data['s_tml_nam']
            if 's_tml_cod' in api_response_data:
                record_data['s_tml_cod'] = api_response_data['s_tml_cod']
            if 'tml_nam' in api_response_data:
                record_data['tml_nam'] = api_response_data['tml_nam']
            if 'tml_cod' in api_response_data:
                record_data['tml_cod'] = api_response_data['tml_cod']
            if 'cen_nam' in api_response_data:
                record_data['cen_nam'] = api_response_data['cen_nam']
            if 'cen_cod' in api_response_data:
                record_data['cen_cod'] = api_response_data['cen_cod']
            if 'pd_tim' in api_response_data:
                record_data['pd_tim'] = api_response_data['pd_tim']
            if 'dom_rgn' in api_response_data:
                record_data['dom_rgn'] = api_response_data['dom_rgn']
            if 'hub_cod' in api_response_data:
                record_data['hub_cod'] = api_response_data['hub_cod']
            if 'dom_mid' in api_response_data:
                record_data['dom_mid'] = api_response_data['dom_mid']
            if 'es_cod' in api_response_data:
                record_data['es_cod'] = api_response_data['es_cod']
            if 'grp_rnk' in api_response_data:
                record_data['grp_rnk'] = api_response_data['grp_rnk']
            if 'es_nam' in api_response_data:
                record_data['es_nam'] = api_response_data['es_nam']
            if 'wbl_num' in api_response_data:
                record_data['wbl_num'] = api_response_data['wbl_num']
            
            # HanjinPrintwbls 객체 생성
            printwbls_record = HanjinPrintwbls(**record_data)
            
            self.session.add(printwbls_record)
            await self.session.commit()
            await self.session.refresh(printwbls_record)
            
            logger.info(f"API 응답 기반 hanjin_printwbls 레코드 생성 성공: idx={idx}, msg_key={printwbls_record.msg_key}")
            return printwbls_record
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"API 응답 기반 hanjin_printwbls 레코드 생성 실패: {str(e)}")
            raise
        finally:
            await self.session.close()