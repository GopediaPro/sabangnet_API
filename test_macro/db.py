import xml.etree.ElementTree as ET

xml_string = """<?xml version="1.0" encoding="euc-kr"?>
 <SABANG_RESULT>
                <HEADER>
                        <SEND_COMPAYNY_ID>okokmart_kha</SEND_COMPAYNY_ID>
                        <SEND_DATE><![CDATA[20250708]]></SEND_DATE>
                        <TOTAL_COUNT>4</TOTAL_COUNT>
                </HEADER>
                <DATA>
                        <RESULT>SUCCESS</RESULT>
                        <MODE>수정</MODE>
                        <PRODUCT_ID><![CDATA[129841]]></PRODUCT_ID>
                </DATA>
                <DATA>
                        <RESULT>SUCCESS</RESULT>
                        <MODE>수정</MODE>
                        <PRODUCT_ID><![CDATA[129838]]></PRODUCT_ID>
                </DATA>
                <DATA>
                        <RESULT>SUCCESS</RESULT>
                        <MODE>수정</MODE>
                        <PRODUCT_ID><![CDATA[129839]]></PRODUCT_ID>
                </DATA>
                <DATA>
                        <RESULT>SUCCESS</RESULT>
                        <MODE>수정</MODE>
                        <PRODUCT_ID><![CDATA[129840]]></PRODUCT_ID>
                </DATA>
        </SABANG_RESULT>
"""

# XML 문자열을 ElementTree 객체로 파싱
root = ET.fromstring(xml_string)
# 모든 'item' 요소 찾기
datas = root.findall('DATA')

for data in datas:
    # 'item' 요소의 'id' 속성 추출
    # product_id = item.get('PRODUCT_ID') //attribute 가져오기

    # 'name' 자식 요소의 텍스트 추출 필드 가져오기
    product_id = data.find('PRODUCT_ID').text

    print(f"product_id: {product_id}")
