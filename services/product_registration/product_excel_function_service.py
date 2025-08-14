"""
품번코드대량등록툴 Excel 수식을 Python 메서드로 변환하는 서비스
상품등록 데이터를 기반으로 품번코드대량등록툴 데이터를 생성합니다.
"""

from typing import Dict, Any, Optional, List
import math
from utils.logs.sabangnet_logger import get_logger
from repository.product_mycategory_repository import ProductMyCategoryRepository

logger = get_logger(__name__)

class ProductCodeRegistrationService:
    """품번코드대량등록툴 Excel 수식 변환 서비스"""
    
    def __init__(self, product_registration_raw_data: Dict[str, Any], class_cd_dict: Dict[str, str]):
        """
        Args:
            product_registration_data: 상품등록 테이블의 데이터 (K열~AH열에 해당하는 데이터)
            class_cd_dict: 카테고리 코드 딕셔너리
        """
        self.source_data = product_registration_raw_data
        self.class_cd_dict = class_cd_dict
    
    def generate_product_code_data(self, product_nm: str, gubun: str) -> Dict[str, Any]:
        """
        Args:
            product_nm: 모델명 (F에 해당)
            gubun: 구분 (G에 해당) - "마스터", "전문몰", "1+1"
            
        Returns:
            품번코드대량등록툴 형식의 데이터 딕셔너리
        """
        try:
            result = {}
            
            # 순번 (A)
            result['no_product'] = 1
            
            # 대표이미지확인 (B) - =image(AM5,2)
            # result['img_path'] = "IMG 없음"
            # self._get_representative_image_check(gubun)
            
            # 상세이미지확인 (C) - =IMAGE(VLOOKUP(F5,'상품등록'!$K:$AH,22,0),2)
            result['detail_img_url'] = self._get_detail_image_check(product_nm)
            
            # 글자수 (D) - =lenb(H5)
            result['no_word'] = self._get_byte_length(product_nm, gubun)
            
            # 키워드 Byte (E) - =LEN(N5)
            result['no_keyword'] = self._get_keyword_length(product_nm)
            
            # 모델명 (F)
            result['product_nm'] = product_nm
            
            # 구분 (G)
            result['gubun'] = gubun
            
            # 상품명[필수] (H)
            result['goods_nm'] = self._get_product_name(product_nm, gubun)
            
            # 상품약어 (I)
            result['goods_keyword'] = self._get_product_abbreviation(product_nm, gubun)
            
            # 모델명 (J)
            result['model_nm'] = self._get_model_name(product_nm, gubun)
            
            # 모델NO (K)
            result['model_no'] = self._get_model_no(product_nm, gubun)
            
            # 브랜드명 (L)
            result['brand_nm'] = "OMT"
            
            # 자체상품코드 (M)
            result['compayny_goods_cd'] = self._get_company_goods_cd(product_nm, gubun)
            
            # 사이트검색어 (N)
            result['goods_search'] = self._get_site_search_word(product_nm)
            
            # 표준카테고리 (O)
            # TODO 표준카테고리 코드 알아보기 - 사방넷 - 기본정보 -> 표준카테고리 관리 참고 
            # result['표준카테고리'] = ""
            
            # 상품구분[필수] (P)
            result['goods_gubun'] = self._get_product_classification(product_nm)
            
            # 마이카테고리 (Q)
            # TODO 마이카테고리 코드 알아보기 - 사방넷 - 기본정보 -> 마이카테고리 관리 참고
            # result['마이카테고리'] = ""
            
            # 매입처ID (R)
            result['partner_id'] = self._get_purchase_partner_id(gubun)
            
            # 물류처ID (S)
            result['dpartner_id'] = "okmart"
            
            # 제조사[필수] (T)
            result['maker'] = "(주)오케이마트"
            
            # 원산지(제조국)[필수] (U)
            result['origin'] = "중국"
            
            # 생산연도 (V) (YYYY)
            result['make_year'] = ""
            
            # 제조일 (W) (YYYYMMDD)
            result['make_dm'] = ""
            
            # 시즌 (X)
            result['goods_season'] = None
            
            # 남녀구분 (Y)
            result['sex'] = None
            
            # 상품상태[필수] (Z)
            """▶상품상태를 숫자로 입력합니다. 대기중 : 1, 공급중 : 2, 일시중지 : 3, 완전품절 : 4, 미사용 : 5, 삭제 : 6, 자료없음 : 7"""
            result['status'] = 2
            
            # 판매지역 (AA)
            """ 전국 : 1, 전국(도서제외) : 2, 수도권 : 3, 기타 : 4"""
            result['deliv_able_region'] = 1
            
            # 세금구분[필수] (AB)
            """▶세금구분을 숫자로 입력합니다. 과세 : 1, 면세 : 2, 자료없음 : 3, 비과세 : 4, 영세 : 5"""
            result['tax_yn'] = 1
            
            # 배송비구분[필수] (AC)
            """▶배송비구분을 숫자로 입력합니다. 무료 : 1, 유료 : 2, 선결제 : 3, 착불/선결제: 4, 자료없음 : 5"""
            result['delv_type'] = 3
            
            # 배송비 (AD)
            result['delv_cost'] = 3000
            
            # 반품지구분 (AE)
            result['banpum_area'] = None
            
            # 원가[필수] (AF)
            result['goods_cost'] = None
            
            # 판매가[필수] (AG)    
            result['goods_price'] = self._get_selling_price(product_nm, gubun)

            result['stock_use_yn'] = "N"
            logger.info(f"stock_use_yn 처리 - source_data: {self.source_data.get('stock_use_yn')}, result: {result['stock_use_yn']}")
            
            # TAG가[필수] (AH)
            result['goods_consumer_price'] = self._get_tag_price(product_nm, gubun)
            
            # 옵션제목(1) (AI)
            result['char_1_nm'] = self._get_option_title_1()
            
            # 옵션상세명칭(1) (AJ)
            result['char_1_val'] = self._get_option_detail_1(product_nm, gubun)
            
            # 옵션제목(2) (AK)
            result['char_2_nm'] = self._get_option_title_2(product_nm, gubun)
            
            # 옵션상세명칭(2) (AL)
            result['char_2_val'] = self._get_option_detail_2(product_nm, gubun)
            
            # 대표이미지[필수] (AM)
            # self._get_representative_image_check(gubun)
            result['img_path'] = self._get_representative_image(product_nm, gubun)
            
            # 종합몰(JPG)이미지 (AN)
            result['img_path1'] = self._get_mall_jpg_image(product_nm, gubun, 1)
            
            # 부가이미지들 (AO~AW) - 빈 값으로 설정
            for i in range(2, 5):
                result[f'img_path{i}'] = self._get_mall_jpg_image(product_nm, gubun, i)
            for i in range(6, 11):
                result[f'img_path{i}'] = self._get_mall_jpg_image(product_nm, gubun, i)

            # 상품상세설명[필수] (AX)
            result['goods_remarks'] = self._get_product_detail_description(product_nm, gubun)

            # TODO 추가상품그룹 관리 - 사방넷 - 상품관리 -> 추가상품그룹 관리 참고 - 자료 없음. 
            # 추가상품그룹코드 (AY)
            
            # 기타 항목
            # 인증번호 (AZ)
            # 인증유효시작일 (BA)
            # 인증유효마지막일 (BB)
            # 발급일자 (BC)
            # 인증일자 (BD)
            # 인증기관 (BE)
            # 인증분야 (BF)
            # 재고관리사용여부 (BG)
            # 유효일 (BH)
            # 식품재료/원산지 (BI)
            # 원가2 (BJ)
            # 부가이미지11 (BK ~ BM)
            for i in range(12, 15):
                result[f'img_path{i}'] = self._get_mall_jpg_image(product_nm, gubun, i)
            # 합포시 제외 여부 (BN)
            # 부가이미지14 (BO ~ BW)
            for i in range(14, 23):
                result[f'img_path{i}'] = self._get_mall_jpg_image(product_nm, gubun, i)
            # 관리자메모 (BX)
            # 옵션수정여부 (BY)
            result['opt_type'] = 2
            # 영문 상품명 (BZ)
            # 출력 상품명 (CA)
            # 인증서이미지 (CB)
            # 추가 상품상세설명_1 (CC)
            result['goods_remarks2'] = result['goods_remarks']
            # 추가 상품상세설명_2 (CD)
            # 추가 상품상세설명_3 (CE)
            # 원산지 상세지역 (CF)
            # 수입신고번호 (CG)
            # 수입면장이미지 (CH)
            # 속성 수정 여부 (CH)
            result['prop_edit_yn'] = "Y"
            # 속성분류코드[필수] (CI)
            result['prop1_cd'] = "035"
            # 속성값1~8
            # 속성값들 (기본값 설정) - ProductRawData 모델에는 prop_val1~33까지만 존재
            for i in range(1, 34):
                result[f'prop_val{i}'] = self._get_attr_value(product_nm, i)
            
            # 나머지 필드들은 기본값 또는 빈 값으로 설정
            # result.update(self._get_remaining_fields(product_nm))
            ## 카테고리 관련 추가
            result['class_cd1'] = self._get_category_code_from_class_nm(1)
            result['class_cd2'] = self._get_category_code_from_class_nm(2)
            result['class_cd3'] = self._get_category_code_from_class_nm(3)
            result['class_cd4'] = self._get_category_code_from_class_nm(4)
            
            return result
        except Exception as e:
            logger.error(f"[generate_product_code_data] Error for product_nm='{product_nm}', gubun='{gubun}': {str(e)}")
            raise
    
    def _get_representative_image_check(self, gubun: str) -> str:
        """대표이미지확인 로직"""
        if gubun == "1+1":
            one_plus_one_bn = self.source_data.get('one_plus_one_bn')
            return one_plus_one_bn if one_plus_one_bn else "IMG 없음"
        else:
            return self.source_data.get('img_path')
    
    def _get_detail_image_check(self, product_nm: str) -> str:
        """상세이미지확인 로직"""
        # =IMAGE(VLOOKUP(F5,'상품등록'!$K:$AH,22,0),2)
        # 22번째 컬럼은 goods_remarks_url (상세설명url)
        goods_remarks_url = self.source_data.get('goods_remarks_url', '')
        return goods_remarks_url
    
    def _get_byte_length(self, product_nm: str, gubun: str) -> int:
        """글자수 계산 (바이트 길이)"""
        # =lenb(H5) - H5는 상품명
        product_name = product_nm
        return len(product_name.encode('utf-8'))
    
    def _get_keyword_length(self, product_nm: str) -> int:
        """키워드 길이 계산"""
        # =LEN(N5) - N5는 사이트검색어
        site_search = self._get_site_search_word(product_nm)
        return len(site_search) if site_search else 0
    
    def _get_product_name(self, product_nm: str, gubun: str) -> str:
        """상품명 생성"""
        # Excel 수식:
        # =if(G5="마스터",VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),2,0)&" "&F5,
        #   if(G5="전문몰",VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),2,0),
        #     if(G5="1+1","1+1 "&VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),2,0))))
        goods_nm = self.source_data.get('goods_nm', '')
        
        if gubun == "마스터":
            return f"{goods_nm} {product_nm}"
        elif gubun == "전문몰":
            return goods_nm
        elif gubun == "1+1":
            return f"1+1 {goods_nm}"
        else:
            return goods_nm
    
    def _get_product_abbreviation(self, product_nm: str, gubun: str) -> str:
        """상품약어 생성"""
        # =IF(G5="마스터",F5,IF(G5="전문몰",F5,IF(G5="1+1","1+1 "&F5)))
        if gubun == "마스터":
            return product_nm
        elif gubun == "전문몰":
            return product_nm
        elif gubun == "1+1":
            return f"1+1 {product_nm}"
        else:
            return product_nm
    
    def _get_model_name(self, product_nm: str, gubun: str) -> str:
        """모델명 J열 생성"""
        # =IF(G5="마스터","[마스터]"&F5,IF(G5="전문몰","[전문몰]"&F5,IF(G5="1+1","[마스터]"&"1+1 "&F5)))
        if gubun == "마스터":
            return f"[마스터]{product_nm}"
        elif gubun == "전문몰":
            return f"[전문몰]{product_nm}"
        elif gubun == "1+1":
            return f"[마스터]1+1 {product_nm}"
        else:
            return product_nm
    
    def _get_model_no(self, product_nm: str, gubun: str) -> str:
        """모델NO 생성"""
        # =IF(G5="마스터",F5,IF(G5="전문몰",F5,IF(G5="1+1","1+1 "&F5)))
        if gubun == "마스터":
            return product_nm
        elif gubun == "전문몰":
            return product_nm
        elif gubun == "1+1":
            return f"1+1 {product_nm}"
        else:
            return product_nm
    def _get_company_goods_cd(self, product_nm: str, gubun: str) -> str:
        """자체상품코드 생성"""
        # =IF(G5="마스터","[OMT]"&F5,IF(G5="전문몰",F5,IF(G5="1+1","1+1 "&F5)))
        if gubun == "마스터":
            return f"[OMT]{product_nm}"
        elif gubun == "전문몰":
            return f"{product_nm}"
        elif gubun == "1+1":
            return f"1+1 {product_nm}"
        else:
            return product_nm
    
    def _get_site_search_word(self, product_nm: str) -> str:
        """사이트검색어 조회"""
        # =VLOOKUP(F5,'상품등록'!$K:$AH,5,0)
        # 5번째 컬럼은 goods_search
        return self.source_data.get('goods_search', '')
    
    def _get_product_classification(self, product_nm: str) -> str:
        """상품구분 조회"""
        # =IF(F5<>"", 5, "") => F5 셀에 값이 있으면 5를 표시하고, F5 셀이 비어있으면 아무것도 표시하지 않는다
        if product_nm:
            return 5
        else:
            return 0
    
    def _get_purchase_partner_id(self, gubun: str) -> str:
        """매입처ID 생성"""
        # =if(G5="마스터","okokmart01",if(G5="전문몰","okokmart60",if(G5="1+1","okokmart01")))
        if gubun == "마스터":
            return "okokmart01"
        elif gubun == "전문몰":
            return "okokmart60"
        elif gubun == "1+1":
            return "okokmart01"
        else:
            return "okokmart01"
    
    def _get_selling_price(self, product_nm: str, gubun: str) -> int:
        """판매가 계산"""
        # =IF(G5="마스터",VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),6,0)+100,
        #   IF(G5="전문몰",VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),6,0),
        #     IF(G5="1+1",VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),6,0)*2+2000)))
        
        base_price = self.source_data.get('goods_price', 0)
        
        # None 체크 및 타입 변환
        if base_price is None:
            base_price = 0
        elif isinstance(base_price, str):
            base_price = int(base_price) if base_price.isdigit() else 0
        elif isinstance(base_price, (int, float)):
            base_price = int(base_price)
        else:
            base_price = 0
        
        if gubun == "마스터":
            return base_price + 100
        elif gubun == "전문몰":
            return base_price
        elif gubun == "1+1":
            return base_price * 2 + 2000
        else:
            return base_price
    
    def _get_tag_price(self, product_nm: str, gubun: str) -> int:
        """TAG가 조회"""
        # 전반적으로 20% 수정 & 1000단위 반올림
        # =IF(G5="마스터",AG5+(AG5*60%),
        #   IF(G5="전문몰",ROUNDUP((AG5+100+3000)+((AG5+100+3000)*60%),-3),
        #     IF(G5="1+1",ROUNDUP((AG5+(AG5*60%)),-3))))
        
        cost_price = self._get_selling_price(product_nm, gubun)
        
        if gubun == "마스터":
            total_cost = cost_price + 3000
            selling_price = total_cost + (total_cost * 0.2)
            # ROUNDUP to nearest 1000
            return math.ceil(selling_price / 1000) * 1000
        elif gubun == "전문몰":
            total_cost = cost_price + 100 + 3000
            selling_price = total_cost + (total_cost * 0.2)
            # ROUNDUP to nearest 1000
            return math.ceil(selling_price / 1000) * 1000
        elif gubun == "1+1":
            selling_price = cost_price + (cost_price * 0.2)
            # ROUNDUP to nearest 1000
            return math.ceil(selling_price / 1000) * 1000
        else:
            return cost_price
    
    def _get_option_title_1(self) -> str:
        """옵션제목(1) 조회"""
        # =VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),9,0)
        # 9번째 컬럼에 해당하는 데이터를 찾아야 함 (추정: 관련 가격 정보)
        char_1_nm = self.source_data.get('char_1_nm', '')
        return char_1_nm if char_1_nm else "옵션제목 없음"
    
    def _get_option_detail_1(self, product_nm: str, gubun: str) -> str:
        """옵션상세명칭(1) 조회"""
        # =IF(G5="마스터",VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),10,0),
        #   IF(G5="전문몰",TEXTJOIN(",",TRUE, ARRAYFORMULA(INDEX(SPLIT(F5,"-"), 2)&"_"&SPLIT(VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),10,0),","))),
        #     IF(G5="1+1",(VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),24,0)))))
        # 10번째 컬럼은 char_1_nm
        # product_nm 에서 '-' 기준으로 뒤에 있는 값을 가져옴 '-'이 없으면 product_nm 그대로 사용
        model_nm = product_nm.split('-')[1] if '-' in product_nm else product_nm
        # model_nm 와 delv_one_plus_one을 가져와서 delv_one_plus_one의 구분자 ','를 기준으로 모든 값들의 앞에 model_nm에 '_'를 붙여서 합치기  
        delv_one_plus_one = self.source_data.get('delv_one_plus_one', '')
        if delv_one_plus_one and delv_one_plus_one.strip():
            # 구분자 ','를 기준으로 값들을 분리
            values = [val.strip() for val in delv_one_plus_one.split(',') if val.strip()]
            # 각 값 앞에 model_nm_을 붙여서 합치기
            delv_one_plus_one_detail = ','.join([f"{model_nm}_{val}" for val in values])
            logger.info(f"옵션상세명칭(1) 조회 delv_one_plus_one_detail: {delv_one_plus_one_detail}")
        else:
            delv_one_plus_one_detail = ''
        
        # 옵션상세명칭(1) 조회
        
        
        if gubun == "마스터":
            char_1_val = self.source_data.get('char_1_val', '')
            return char_1_val if char_1_val is not None else ''
        elif gubun == "전문몰":
            # TEXTJOIN 로직 구현 필요
            char_1_val = self.source_data.get('char_1_val', '')
            if char_1_val and char_1_val is not None:
                model_suffix = product_nm.split('-')[1] if '-' in product_nm else ''
                values = char_1_val.split(',')
                return ','.join([f"{model_suffix}_{val.strip()}" for val in values])
            return ''
        elif gubun == "1+1":
            # 24번째 컬럼에 해당하는 값
            return delv_one_plus_one_detail if delv_one_plus_one_detail is not None else ''
    
    def _get_option_title_2(self, product_nm: str, gubun: str) -> str:
        """옵션제목(2) 조회"""
        # =IF(G6="마스터",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),11,0),
        #   IF(G6="전문몰",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),11,0),
        #     IF(G6="1+1",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),9,0))))
        # 11번째 컬럼은 char_2_nm
        if gubun in ["마스터", "전문몰"]:
            return self.source_data.get('char_2_nm', '')
        elif gubun == "1+1":
            # 9번째 컬럼으로 대체
            return self.source_data.get('char_1_nm', '')
    
    def _get_option_detail_2(self, product_nm: str, gubun: str) -> str:
        """옵션상세명칭(2) 조회"""
        # =IF(G6="마스터",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),12,0),
        #   IF(G6="전문몰",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),12,0),
        #     IF(G6="1+1",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),23,0))))
        # 12번째 컬럼은 char_2_val
        if gubun in ["마스터", "전문몰"]:
            char_2_val = self.source_data.get('char_2_val', '')
            return char_2_val if char_2_val is not None else ''
        elif gubun == "1+1":
            # 23번째 컬럼으로 대체 (추정)
            delv_one_plus_one = self.source_data.get('delv_one_plus_one', '')
            return delv_one_plus_one if delv_one_plus_one is not None else '' 
    
    def _get_representative_image(self, product_nm: str, gubun: str) -> str:
        """대표이미지 조회"""
        # =IF(G6="마스터",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),13,0),
        #   IF(G6="전문몰",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),13,0),
        #     IF(G6="1+1",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),21,0))))
        # 13번째 컬럼은 img_path
        if gubun in ["마스터", "전문몰"]:
            return self.source_data.get('img_path', '')
        elif gubun == "1+1":
            # 21번째 컬럼으로 대체
            return self.source_data.get('one_plus_one_bn', '') 
    
    def _get_mall_jpg_image(self, product_nm: str, gubun: str, i: int) -> str:
        """종합몰(JPG)이미지 조회"""
        # =IF(G6="마스터",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),13,0),
        #   IF(G6="전문몰",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),13,0),
        #     IF(G6="1+1",VLOOKUP(F6,importrange("same file","상품등록!$k:$az"),21,0))))
        # 13번째 컬럼은 img_path
        # i = 6 ~ 10까지는 img_path1 ~ img_path5로 대체
        if i == 6:
            return self.source_data.get('img_path1', '')
        elif i == 7:
            return self.source_data.get('img_path2', '')
        elif i == 8:
            return self.source_data.get('img_path3', '')
        elif i == 9:
            return self.source_data.get('img_path4', '')
        elif i == 10:
            return self.source_data.get('img_path5', '')
        if i == 21:
            return self.source_data.get('mobile_bn', '')
        elif gubun in ["마스터", "전문몰"]:
            return self.source_data.get('img_path', '')
        elif gubun == "1+1":
            # 21번째 컬럼으로 대체
            return self.source_data.get('one_plus_one_bn', '')

    
    def _get_product_detail_description(self, product_nm: str, gubun: str) -> str:
        """상품상세설명 조회"""
        # =VLOOKUP(F5,importrange("same file","상품등록!$k:$az"),19,0)
        # 19번째 컬럼은 goods_remarks
        goods_remarks = self.source_data.get('goods_remarks', '')
        if goods_remarks and goods_remarks is not None:
            return goods_remarks
        else:
            return "상세설명 URL 없음"
        
    def _get_attr_value(self, product_nm: str, i: int) -> str:
        """속성값 조회"""
        if i == 2:
            return "(주)오케이마트/(주)오케이마트"
        elif i == 3:
            return "중국"
        elif i == 6:
            return "(주)오케이마트/02-802-7447"
        elif i == 8:
            return "해당사항없음"
        else:
            return "상세페이지참조"
    def _get_category_code_from_class_nm(self, level: int) -> str:
        """카테고리코드 조회"""
        return self.class_cd_dict.get(f'class_cd{level}', '')

    def _get_remaining_fields(self, product_nm: str) -> Dict[str, str]:
        """나머지 필드들의 기본값"""
        remaining = {}
        
        return remaining

def create_bulk_product_code_data(source_data_list: List[Dict[str, Any]], 
                                  product_nms_with_gubun: List[tuple],
                                  class_cd_dict: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    여러 상품에 대한 품번코드대량등록툴 데이터를 일괄 생성
    
    Args:
        source_data_list: 상품등록 테이블의 데이터 리스트
        product_nms_with_gubun: (product_nm, gubun) 튜플 리스트
        
    Returns:
        품번코드대량등록툴 형식의 데이터 리스트
    """
    try:
        results = []
        
        # 상품등록 데이터를 product_nm 기준으로 인덱싱
        source_data_dict = {}
        for data in source_data_list:
            # 모델코드에 해당하는 키를 찾아야 함 (실제 DB 스키마에 따라 조정 필요)
            model_key = data.get('product_nm', '') or data.get('product_nm', '')
            if model_key:
                source_data_dict[model_key] = data
        
        for product_nm, gubun in product_nms_with_gubun:
            source_data = source_data_dict.get(product_nm, {})
            
            service = ProductCodeRegistrationService(source_data, class_cd_dict)
            result = service.generate_product_code_data(product_nm, gubun)
            results.append(result)
        
        return results
    except Exception as e:
        logger.error(f"[create_bulk_product_code_data] Error: {str(e)}")
        raise
