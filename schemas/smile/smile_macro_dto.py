from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SmileMacroDto(BaseModel):
    """
    스마일배송 매크로 DTO
    column.txt 파일의 컬럼 정보를 기반으로 생성
    """
    
    # 기본 정보
    정산완료일: Optional[str] = Field(None, description="정산완료일")
    아이디: Optional[str] = Field(None, description="아이디")
    상품번호: Optional[str] = Field(None, description="상품번호")
    주문번호: Optional[str] = Field(None, description="주문번호")
    SKU번호_및_수량: Optional[str] = Field(None, description="SKU번호 및 수량")
    판매단가: Optional[str] = Field(None, description="판매단가")
    주문확인일자: Optional[str] = Field(None, description="주문확인일자")
    결제완료일: Optional[str] = Field(None, description="결제완료일")
    배송상태: Optional[str] = Field(None, description="배송상태")
    상품명: Optional[str] = Field(None, description="상품명")
    주문옵션: Optional[str] = Field(None, description="주문옵션")
    수량: Optional[str] = Field(None, description="수량")
    판매금액: Optional[str] = Field(None, description="판매금액")
    서비스_이용료: Optional[str] = Field(None, description="서비스 이용료")
    구매자명: Optional[str] = Field(None, description="구매자명")
    수령인명: Optional[str] = Field(None, description="수령인명")
    주소: Optional[str] = Field(None, description="주소")
    구매자_전화번호: Optional[str] = Field(None, description="구매자 전화번호")
    구매자_휴대폰: Optional[str] = Field(None, description="구매자 휴대폰")
    수령인_전화번호: Optional[str] = Field(None, description="수령인 전화번호")
    수령인_휴대폰: Optional[str] = Field(None, description="수령인 휴대폰")
    배송번호: Optional[str] = Field(None, description="배송번호")
    배송비: Optional[str] = Field(None, description="배송비")
    배송비_금액: Optional[str] = Field(None, description="배송비 금액")
    구매결정일자: Optional[str] = Field(None, description="구매결정일자")
    구매쿠폰적용금액: Optional[str] = Field(None, description="구매쿠폰적용금액")
    배송구분: Optional[str] = Field(None, description="배송구분")
    배송시_요구사항: Optional[str] = Field(None, description="배송시 요구사항")
    배송완료일자: Optional[str] = Field(None, description="배송완료일자")
    발송예정일: Optional[str] = Field(None, description="발송예정일")
    발송일자: Optional[str] = Field(None, description="발송일자")
    배송지연사유: Optional[str] = Field(None, description="배송지연사유")
    배송점포: Optional[str] = Field(None, description="배송점포")
    상품미수령상세사유: Optional[str] = Field(None, description="상품미수령상세사유")
    상품미수령신고사유: Optional[str] = Field(None, description="상품미수령신고사유")
    상품미수령신고일자: Optional[str] = Field(None, description="상품미수령신고일자")
    상품미수령이의제기일자: Optional[str] = Field(None, description="상품미수령이의제기일자")
    상품미수령철회요청일자: Optional[str] = Field(None, description="상품미수령철회요청일자")
    송장번호: Optional[str] = Field(None, description="송장번호(방문수령인증키)")
    우편번호: Optional[str] = Field(None, description="우편번호")
    일시불할인: Optional[str] = Field(None, description="일시불할인")
    장바구니번호: Optional[str] = Field(None, description="장바구니번호(결제번호)")
    재배송일: Optional[str] = Field(None, description="재배송일")
    재배송지_우편번호: Optional[str] = Field(None, description="재배송지 우편번호")
    재배송지_운송장번호: Optional[str] = Field(None, description="재배송지 운송장번호")
    재배송지_주소: Optional[str] = Field(None, description="재배송지 주소")
    재배송택배사명: Optional[str] = Field(None, description="재배송택배사명")
    정산예정금: Optional[str] = Field(None, description="정산예정금")
    주문일자: Optional[str] = Field(None, description="주문일자(결제확인전)")
    주문종류: Optional[str] = Field(None, description="주문종류")
    택배사명: Optional[str] = Field(None, description="택배사명(발송방법)")
    판매방식: Optional[str] = Field(None, description="판매방식")
    판매자_관리코드: Optional[str] = Field(None, description="판매자 관리코드")
    판매자_상세관리코드: Optional[str] = Field(None, description="판매자 상세관리코드")
    판매자북캐시적립: Optional[str] = Field(None, description="판매자북캐시적립")
    판매자쿠폰할인: Optional[str] = Field(None, description="판매자쿠폰할인")
    판매자포인트적립: Optional[str] = Field(None, description="판매자포인트적립")
    복수구매할인: Optional[str] = Field(None, description="(옥션)복수구매할인")
    우수회원할인: Optional[str] = Field(None, description="(옥션)우수회원할인")
    추가구성: Optional[str] = Field(None, description="추가구성")
    사은품: Optional[str] = Field(None, description="사은품")
    구매자ID: Optional[str] = Field(None, description="구매자ID")
    
    # 매크로 처리 후 추가되는 필드들
    ERP매칭: Optional[str] = Field(None, description="ERP 매칭 결과")
    정산여부: Optional[str] = Field(None, description="정산 여부")
    모델명_수량: Optional[str] = Field(None, description="모델명+수량")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


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