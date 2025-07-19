from typing import Any


MALL_INFO: list[dict[str, Any]] = [
    {
        "id": 1,
        "mall_id": "GS shop",
        "shop_code": "shop0007",
    },
    {
        "id": 2,
        "mall_id": "YES24",
        "shop_code": "shop0029",
    },
    {
        "id": 3,
        "mall_id": "텐바이텐",
        "shop_code": "shop0042",
    },
    {
        "id": 4,
        "mall_id": "스마트스토어",
        "shop_code": "shop0055",
    },
    {
        "id": 5,
        "mall_id": "ESM옥션",
        "shop_code": "shop0067",
    },
    {
        "id": 6,
        "mall_id": "ESM지마켓",
        "shop_code": "shop0068",
    },
    {
        "id": 7,
        "mall_id": "쿠팡",
        "shop_code": "shop0075",
    },
    {
        "id": 8,
        "mall_id": "롯데홈쇼핑(신)",
        "shop_code": "shop0087",
    },
    {
        "id": 9,
        "mall_id": "무신사",
        "shop_code": "shop0094",
    },
    {
        "id": 10,
        "mall_id": "신세계몰(신)",
        "shop_code": "shop0100",
    },
    {
        "id": 11,
        "mall_id": "NS홈쇼핑(신)",
        "shop_code": "shop0121",
    },
    {
        "id": 12,
        "mall_id": "CJ온스타일",
        "shop_code": "shop0129",
    },
    {
        "id": 13,
        "mall_id": "K쇼핑",
        "shop_code": "shop0154",
    },
    {
        "id": 14,
        "mall_id": "오늘의집",
        "shop_code": "shop0189",
    },
    {
        "id": 15,
        "mall_id": "카카오톡스토어",
        "shop_code": "shop0273",
    },
    {
        "id": 16,
        "mall_id": "Cafe24(신) 유튜브쇼핑",
        "shop_code": "shop0298",
    },
    {
        "id": 17,
        "mall_id": "도매꾹",
        "shop_code": "shop0319",
    },
    {
        "id": 18,
        "mall_id": "브랜디",
        "shop_code": "shop0322",
    },
    {
        "id": 19,
        "mall_id": "Grip",
        "shop_code": "shop0365",
    },
    {
        "id": 20,
        "mall_id": "롯데온",
        "shop_code": "shop0372",
    },
    {
        "id": 21,
        "mall_id": "에이블리",
        "shop_code": "shop0381",
    },
    {
        "id": 22,
        "mall_id": "하프클럽(신)",
        "shop_code": "shop0387",
    },
    {
        "id": 23,
        "mall_id": "아트박스(신)",
        "shop_code": "shop0416",
    },
    {
        "id": 24,
        "mall_id": "카카오스타일 (지그재그, 포스티)",
        "shop_code": "shop0444",
    },
    {
        "id": 25,
        "mall_id": "카카오톡선물하기(신)",
        "shop_code": "shop0449",
    },
    {
        "id": 26,
        "mall_id": "11번가",
        "shop_code": "shop0464",
    },
    {
        "id": 27,
        "mall_id": "올웨이즈",
        "shop_code": "shop0498",
    },
    {
        "id": 28,
        "mall_id": "토스쇼핑",
        "shop_code": "shop0583",
    },
    {
        "id": 29,
        "mall_id": "AliExpress",
        "shop_code": "shop0587",
    },
    {
        "id": 30,
        "mall_id": "홈&쇼핑(신)",
        "shop_code": "shop0650",
    },
    {
        "id": 31,
        "mall_id": "떠리몰",
        "shop_code": "shop0661",
    }
]

# 몰 코드와 이름 매핑 딕셔너리
MALL_CODE_NAME_MAPPING: dict[str, str] = {
    "shop0007": "GS shop",
    "shop0029": "YES24",
    "shop0042": "텐바이텐",
    "shop0055": "스마트스토어",
    "shop0067": "ESM옥션",
    "shop0068": "ESM지마켓",
    "shop0075": "쿠팡",
    "shop0087": "롯데홈쇼핑(신)",
    "shop0094": "무신사",
    "shop0100": "신세계몰(신)",
    "shop0121": "NS홈쇼핑(신)",
    "shop0129": "CJ온스타일",
    "shop0154": "K쇼핑",
    "shop0189": "오늘의집",
    "shop0273": "카카오톡스토어",
    "shop0298": "Cafe24(신) 유튜브쇼핑",
    "shop0319": "도매꾹",
    "shop0322": "브랜디",
    "shop0365": "Grip",
    "shop0372": "롯데온",
    "shop0381": "에이블리",
    "shop0387": "하프클럽(신)",
    "shop0416": "아트박스(신)",
    "shop0444": "카카오스타일 (지그재그, 포스티)",
    "shop0449": "카카오톡선물하기",
    "shop0464": "11번가",
    "shop0498": "올웨이즈",
    "shop0583": "토스쇼핑",
    "shop0587": "AliExpress",
    "shop0650": "홈&쇼핑(신)",
    "shop0661": "떠리몰"
}

# 몰 이름과 코드 매핑 딕셔너리 (역방향)
MALL_NAME_CODE_MAPPING: dict[str, str] = {
    "GS shop": "shop0007",
    "YES24": "shop0029",
    "텐바이텐": "shop0042",
    "스마트스토어": "shop0055",
    "ESM옥션": "shop0067",
    "ESM지마켓": "shop0068",
    "쿠팡": "shop0075",
    "롯데홈쇼핑(신)": "shop0087",
    "무신사": "shop0094",
    "신세계몰(신)": "shop0100",
    "NS홈쇼핑(신)": "shop0121",
    "CJ온스타일": "shop0129",
    "K쇼핑": "shop0154",
    "오늘의집": "shop0189",
    "카카오톡스토어": "shop0273",
    "Cafe24(신) 유튜브쇼핑": "shop0298",
    "도매꾹": "shop0319",
    "브랜디": "shop0322",
    "Grip": "shop0365",
    "롯데온": "shop0372",
    "에이블리": "shop0381",
    "하프클럽(신)": "shop0387",
    "아트박스(신)": "shop0416",
    "카카오스타일 (지그재그, 포스티)": "shop0444",
    "카카오톡선물하기": "shop0449",
    "11번가": "shop0464",
    "올웨이즈": "shop0498",
    "토스쇼핑": "shop0583",
    "AliExpress": "shop0587",
    "홈&쇼핑(신)": "shop0650",
    "떠리몰": "shop0661"
}
