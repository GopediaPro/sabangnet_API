PRODUCT_CREATE_FIELD_MAPPING = {
    # "순번": "", -> 디자인업무일지 O 명세서 X
    # "대표이미지확인": "", -> 디자인업무일지 O 명세서 X
    # "상세이미지확인": "", -> 디자인업무일지 O 명세서 X
    # "글자수": "", -> 디자인업무일지 O 명세서 X
    # "키워드": "", -> 디자인업무일지 O 명세서 X
    # "모델명": "", -> 디자인업무일지 O 명세서 X
    # "구분": "", -> 디자인업무일지 O 명세서 X

    # 기본 상품 정보
    "상품명": "GOODS_NM",
    "상품약어": "GOODS_KEYWORD", 
    "모델명": "MODEL_NM",
    "모델NO": "MODEL_NO",
    "브랜드명": "BRAND_NM",
    "자체상품코드": "COMPAYNY_GOODS_CD",
    "사이트검색어": "GOODS_SEARCH",

    # 분류·구분 코드
    # "표준카테고리": "", -> 디자인업무일지 O 명세서 X
    "상품구분": "GOODS_GUBUN",
    "마이카테고리": ("CLASS_CD1", "CLASS_CD2", "CLASS_CD3", "CLASS_CD4"), # -> 디자인업무일지 O 명세서 X, 그러나 분리되서 들어가짐

    # 거래처
    "매입처ID": "PARTNER_ID",
    "물류처ID": "DPARTNER_ID",

    # 제조·원산지
    "제조사": "MAKER",
    "원산지(제조국)": "ORIGIN",
    "생산연도": "MAKE_YEAR",
    "제조일": "MAKE_DM",

    # 시즌·성별·상태
    "시즌": "GOODS_SEASON",
    "남녀구분": "SEX",
    "상품상태": "STATUS",

    # 배송·세금
    "판매지역": "DELIV_ABLE_REGION",
    "세금구분": "TAX_YN",
    "배송비구분": "DELV_TYPE",
    "배송비": "DELV_COST",

    # 반품·가격
    "반품지구분": "BANPUM_AREA",
    "원가": "GOODS_COST",
    "판매가": "GOODS_PRICE",
    "TAG가": "GOODS_CONSUMER_PRICE",


    # 옵션
    "옵션제목(1)": "CHAR_1_NM",
    "옵션상세명칭(1)": "CHAR_1_VAL",
    "옵션제목(2)": "CHAR_2_NM", 
    "옵션상세명칭(2)": "CHAR_2_VAL",

    # 이미지
    "대표이미지": "IMG_PATH",
    "종합몰(JPG)이미지": "IMG_PATH1",
    "부가이미지2": "IMG_PATH2",
    "부가이미지3": "IMG_PATH3",
    "부가이미지4": "IMG_PATH4",
    "부가이미지5": "IMG_PATH5",
    "부가이미지6": "IMG_PATH6",
    "부가이미지7": "IMG_PATH7",
    "부가이미지8": "IMG_PATH8",
    "부가이미지9": "IMG_PATH9",
    "부가이미지10": "IMG_PATH10",

    # 상세/인증
    "상품상세설명": "GOODS_REMARKS",
    "추가상품그룹코드": "PACK_CODE_STR",
    "인증번호": "CERTNO",
    "인증유효시작일": "AVLST_DM",
    "인증유효마지막일": "AVLED_DM",
    "발급일자": "ISSUEDATE",
    "인증일자": "CERTDATE",
    "인증기관": "CERT_AGENCY",
    "인증분야": "CERTFIELD",
    "재고관리사용여부": "STOCK_USE_YN",
    "유효일": "EXPIRE_DM",

    # 식품·재고
    "식품 재료/원산지": "MATERIAL",
    "원가2": "GOODS_COST2",

    "부가이미지11": "IMG_PATH11",
    "부가이미지12": "IMG_PATH12",
    "부가이미지13": "IMG_PATH13",

    "합포시 제외 여부": "SUPPLY_SAVE_YN",
    
    "부가이미지14": "IMG_PATH14",
    "부가이미지15": "IMG_PATH15",
    "부가이미지16": "IMG_PATH16",
    "부가이미지17": "IMG_PATH17",
    "부가이미지18": "IMG_PATH18",
    "부가이미지19": "IMG_PATH19",
    "부가이미지20": "IMG_PATH20",
    "부가이미지21": "IMG_PATH21",
    "부가이미지22": "IMG_PATH22",
    
    # 기타
    "관리자메모": "DESCRITION",
    "옵션수정여부": "OPT_TYPE",
    # "속성수정여부": "PROP_EDIT_YN" -> 디자인업무일지 X 명세서 O
    "영문 상품명": "GOODS_NM_EN",
    "출력 상품명": "GOODS_NM_PR",
    "인증서이미지": "IMG_PATH23",

    # 옵션·속성 제어
    "추가 상품상세설명_1": "GOODS_REMARKS2",
    "추가 상품상세설명_2": "GOODS_REMARKS3",
    "추가 상품상세설명_3": "GOODS_REMARKS4",
    "원산지 상세지역": "ORIGIN2",
    "수입신고번호": "IMPORTNO",
    "수입면장이미지": "IMG_PATH24",
    "속성분류코드": "PROP1_CD",
    
    # 속성값 1 – 33
    "속성값1": "PROP_VAL1",
    "속성값2": "PROP_VAL2",
    "속성값3": "PROP_VAL3",
    "속성값4": "PROP_VAL4",
    "속성값5": "PROP_VAL5",
    "속성값6": "PROP_VAL6",
    "속성값7": "PROP_VAL7",
    "속성값8": "PROP_VAL8",
    "속성값9": "PROP_VAL9",
    "속성값10": "PROP_VAL10",
    "속성값11": "PROP_VAL11",
    "속성값12": "PROP_VAL12",
    "속성값13": "PROP_VAL13",
    "속성값14": "PROP_VAL14",
    "속성값15": "PROP_VAL15",
    "속성값16": "PROP_VAL16",
    "속성값17": "PROP_VAL17",
    "속성값18": "PROP_VAL18",
    "속성값19": "PROP_VAL19",
    "속성값20": "PROP_VAL20",
    "속성값21": "PROP_VAL21",
    "속성값22": "PROP_VAL22",
    "속성값23": "PROP_VAL23",
    "속성값24": "PROP_VAL24",
    "속성값25": "PROP_VAL25",
    "속성값26": "PROP_VAL26",
    "속성값27": "PROP_VAL27",
    "속성값28": "PROP_VAL28",
    "속성값29": "PROP_VAL29",
    "속성값30": "PROP_VAL30",
    "속성값31": "PROP_VAL31",
    "속성값32": "PROP_VAL32",
    "속성값33": "PROP_VAL33",
    # "속성값34": "PROP_VAL34", -> 디자인업무일지 O 명세서 X
    # "속성값35": "PROP_VAL35", -> 디자인업무일지 O 명세서 X
    # "속성값36": "PROP_VAL36", -> 디자인업무일지 O 명세서 X
    # "속성값37": "PROP_VAL37", -> 디자인업무일지 O 명세서 X
    # "속성값38": "PROP_VAL38", -> 디자인업무일지 O 명세서 X
}