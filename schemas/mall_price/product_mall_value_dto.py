from pydantic import BaseModel, Field
from typing import Optional


class ProductMallValueDto(BaseModel):

    class Config:
        from_attributes = True

    product_nm: Optional[str] = Field(None, description="상품명")
    product_raw_data_id: int = Field(alias="test_product_raw_data_id", description="product_raw_data ID")
    compayny_goods_cd: Optional[str] = Field(None, description="자체 상품 코드")
    standard_price: Optional[int] = Field(None, description="기준 가격")

    # 새로 추가된 필드들
    batch_id: Optional[str] = Field(None, description="배치 ID")
    gubun: Optional[str] = Field(None, description="구분 (전문가/마스터/1+1)")
    mall_prod_name: Optional[str] = Field(None, description="쇼핑몰 상품명")
    mall_prop1_cd: Optional[str] = Field(None, description="쇼핑몰 속성1 코드")
    buinf_id3: Optional[str] = Field(None, description="사업자 정보 ID3")
    mall_stock_rate: Optional[str] = Field(None, description="쇼핑몰 재고율")
    certno: Optional[str] = Field(None, description="인증번호")
    issuedate: Optional[str] = Field(None, description="발급일")
    certdate: Optional[str] = Field(None, description="인증일")
    avlst_dm: Optional[str] = Field(None, description="유효시작일")
    avled_dm: Optional[str] = Field(None, description="유효종료일")
    cert_agency: Optional[str] = Field(None, description="인증기관")
    certfield: Optional[str] = Field(None, description="인증분야")

    # ((기본판매가 + (기본판매가 * 0.15)) 1000자리에서 반올림 후 - 100) + 3000
    shop0007: Optional[int] = Field(None, description="gs shop 가격")
    shop0042: Optional[int] = Field(None, description="텐바이텐 가격")
    shop0087: Optional[int] = Field(None, description="롯데홈쇼핑 가격")
    shop0094: Optional[int] = Field(None, description="무신사 가격")
    shop0121: Optional[int] = Field(None, description="ns홈쇼핑 가격")
    shop0129: Optional[int] = Field(None, description="cj온스타일 가격")
    shop0154: Optional[int] = Field(None, description="k쇼핑 가격")
    shop0650: Optional[int] = Field(None, description="홈&쇼핑 가격")

    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100) + 3000
    shop0029: Optional[int] = Field(None, description="yes24 가격")
    shop0189: Optional[int] = Field(None, description="오늘의집 가격")
    shop0322: Optional[int] = Field(None, description="브랜디 가격")
    shop0444: Optional[int] = Field(None, description="카카오스타일 가격")

    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100)
    shop0100: Optional[int] = Field(None, description="신세계몰(신) 가격")
    shop0298: Optional[int] = Field(None, description="cafe24(신) 가격")
    shop0372: Optional[int] = Field(None, description="롯데온 가격")

    # 기본판매가 + 3000
    shop0381: Optional[int] = Field(None, description="에이블리 가격")
    shop0416: Optional[int] = Field(None, description="아트박스(신) 가격")
    shop0449: Optional[int] = Field(None, description="카카오톡선물하기 가격")
    shop0498: Optional[int] = Field(None, description="올웨이즈 가격")
    shop0583: Optional[int] = Field(None, description="토스쇼핑 가격")
    shop0587: Optional[int] = Field(None, description="aliexpress 가격")
    shop0661: Optional[int] = Field(None, description="떠리몰 가격")

    # 기본판매가 + 100
    shop0055: Optional[int] = Field(None, description="스마트스토어 가격")
    shop0067: Optional[int] = Field(None, description="esm옥션 가격")
    shop0068: Optional[int] = Field(None, description="esm지마켓 가격")
    shop0273: Optional[int] = Field(None, description="카카오톡스토어 가격")
    shop0464: Optional[int] = Field(None, description="11번가 가격")

    # 기본판매가
    shop0075: Optional[int] = Field(None, description="쿠팡 가격")
    shop0319: Optional[int] = Field(None, description="도매꾹 가격")
    shop0365: Optional[int] = Field(None, description="Grip 가격")
    shop0387: Optional[int] = Field(None, description="하프클럽(신) 가격")
