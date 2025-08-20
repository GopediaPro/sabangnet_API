from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class SmileMacroDto(BaseModel):
    """
    스마일배송 매크로 DTO
    SmileMacro 모델을 기반으로 생성
    """
    
    # 기본 정보
    id: Optional[int] = Field(None, description="ID")
    fld_dsp: Optional[str] = Field(None, description="아이디*")
    expected_payout: Optional[int] = Field(None, description="정산예정금")
    service_fee: Optional[int] = Field(None, description="서비스 이용료")
    mall_order_id: Optional[str] = Field(None, description="장바구니번호(결제번호)")
    pay_cost: Optional[int] = Field(None, description="금액[배송비미포함]")
    delv_cost: Optional[int] = Field(None, description="배송비 금액")
    mall_product_id: Optional[str] = Field(None, description="상품번호*")
    order_id: Optional[str] = Field(None, description="주문번호*")
    sku_value: Optional[str] = Field(None, description="주문옵션")
    product_name: Optional[str] = Field(None, description="상품명")
    item_name: Optional[str] = Field(None, description="제품명")
    sale_cnt: Optional[int] = Field(None, description="수량")
    sale_cost: Optional[int] = Field(None, description="판매금액")
    mall_user_id: Optional[str] = Field(None, description="구매자ID")
    user_name: Optional[str] = Field(None, description="구매자명")
    receive_name: Optional[str] = Field(None, description="수령인명")
    delivery_method_str: Optional[str] = Field(None, description="배송비")
    receive_cel: Optional[str] = Field(None, description="수령인 휴대폰")
    receive_tel: Optional[str] = Field(None, description="수령인 전화번호")
    receive_addr: Optional[str] = Field(None, description="주소")
    receive_zipcode: Optional[str] = Field(None, description="우편번호")
    delv_msg: Optional[str] = Field(None, description="배송시 요구사항")
    sku1_no: Optional[str] = Field(None, description="SKU1번호")
    sku1_cnt: Optional[str] = Field(None, description="SKU1수량")
    sku2_no: Optional[str] = Field(None, description="SKU2번호")
    sku2_cnt: Optional[str] = Field(None, description="SKU2수량")
    sku_no: Optional[str] = Field(None, description="SKU번호 및 수량")
    pay_dt: Optional[datetime] = Field(None, description="결제완료일")
    user_tel: Optional[str] = Field(None, description="구매자 전화번호")
    user_cel: Optional[str] = Field(None, description="구매자 휴대폰")
    buy_coupon: Optional[int] = Field(None, description="구매쿠폰적용금액")
    invoice_no: Optional[str] = Field(None, description="배송번호")
    delv_status: Optional[str] = Field(None, description="배송상태")
    order_dt: Optional[datetime] = Field(None, description="주문일자(결제확인전)")
    order_method: Optional[str] = Field(None, description="주문종류")
    delv_method_id: Optional[str] = Field(None, description="택배사명(발송방법)")
    sale_method: Optional[str] = Field(None, description="판매방식")
    order_etc_7: Optional[str] = Field(None, description="판매자 관리코드")
    sale_coupon: Optional[int] = Field(None, description="판매자쿠폰할인")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    
    def to_down_form_order_data(self) -> Dict[str, Any]:
        """
        SmileMacro 데이터를 down_form_order 형식으로 변환하는 builder 메서드
        
        Returns:
            Dict[str, Any]: down_form_order에 저장할 데이터 딕셔너리
        """
        from utils.builders.smile_data_builder import SmileMacroDataBuilder
        from utils.handlers.data_type_handler import SmileDataTypeHandler
        
        common_fields = [
            'fld_dsp', 'receive_name', 'pay_cost', 'order_id', 'item_name', 
            'sale_cnt', 'receive_cel', 'receive_tel', 'receive_addr', 
            'receive_zipcode', 'delivery_method_str', 'mall_product_id', 
            'delv_msg', 'expected_payout', 'service_fee', 'mall_order_id', 
            'order_etc_7', 'sku_no', 'product_name', 'delv_cost', 'invoice_no',
            'sku_value'
        ]
        
        # 필드 타입 매핑 가져오기
        field_types = SmileMacroDataBuilder.get_down_form_order_field_types()
        
        # 공통 필드 데이터 추출 (타입에 맞게 변환)
        mapped_data = {}
        for field in common_fields:
            value = getattr(self, field, None)
            if value is not None:
                field_type = field_types.get(field, 'str')  # 기본값은 문자열
                mapped_data[field] = SmileDataTypeHandler.convert_field_value(
                    value, field, field_type
                )
        
        # form_name 추가
        mapped_data['form_name'] = 'smile'
        # idx 값 추가
        mapped_data['idx'] = mapped_data['order_id']
        # process_dt 값 추가 (datetime 객체로 설정)
        mapped_data['process_dt'] = datetime.now()
        # product_id 값 추가
        mapped_data['product_id'] = mapped_data['mall_product_id']
        
        return mapped_data
    
    @classmethod
    def from_smile_macro_model(cls, smile_macro_model) -> "SmileMacroDto":
        """
        SmileMacro 모델에서 DTO 생성
        
        Args:
            smile_macro_model: SmileMacro 모델 인스턴스
            
        Returns:
            SmileMacroDto: 생성된 DTO 인스턴스
        """
        return cls.model_validate(smile_macro_model)


class SmileMacroRequestDto(BaseModel):
    """
    스마일배송 매크로 요청 DTO
    """
    file_path: str = Field(..., description="처리할 엑셀 파일 경로")
    erp_data: Optional[List[dict]] = Field(None, description="ERP 데이터")
    settlement_data: Optional[List[dict]] = Field(None, description="정산 데이터")
    sku_data: Optional[List[dict]] = Field(None, description="SKU 데이터")
    output_path: Optional[str] = Field(None, description="출력 파일 경로")
    
    model_config = ConfigDict(
        from_attributes=True
    )


class SmileMacroResponseDto(BaseModel):
    """
    스마일배송 매크로 응답 DTO
    """
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="처리 결과 메시지")
    output_path: Optional[str] = Field(None, description="출력 파일 경로 (A 데이터)")
    output_path2: Optional[str] = Field(None, description="출력 파일 경로 (G 데이터)")
    processed_rows: Optional[int] = Field(None, description="처리된 행 수")
    error_details: Optional[str] = Field(None, description="오류 상세 정보")
    batch_id: Optional[int] = Field(None, description="배치 ID")
    macro_handler: Optional[Any] = Field(None, description="매크로 핸들러")
    
    model_config = ConfigDict(
        from_attributes=True
    )


class SmileMacroStageRequestDto(BaseModel):
    """
    스마일배송 매크로 단계별 요청 DTO
    """
    file_path: str = Field(..., description="처리할 엑셀 파일 경로")
    stage: str = Field(..., description="처리할 단계 (1-5, 6-8, all)")
    erp_data: Optional[List[dict]] = Field(None, description="ERP 데이터")
    settlement_data: Optional[List[dict]] = Field(None, description="정산 데이터")
    sku_data: Optional[List[dict]] = Field(None, description="SKU 데이터")
    
    model_config = ConfigDict(
        from_attributes=True
    ) 