from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
from typing import List

from services.product.product_db_xml_service import ProductDbXmlService
from schemas.product.db_xml_dto import (
    DbToXmlByGubunRequest,
    DbToXmlByIdsRequest,
    DbToXmlByProductNmRequest,
    DbToXmlPaginationRequest,
    DbToXmlResponse,
    ProductRawDataCountResponse
)
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/db-xml", tags=["DB to XML"])


@router.post("/all", response_model=DbToXmlResponse)
async def db_to_xml_all():
    """
    test_product_raw_data 테이블의 모든 데이터를 XML로 변환
    """
    try:
        xml_file_path = await ProductDbXmlService.db_to_xml_file_all()
        total_count = await ProductDbXmlService.get_product_raw_data_count()
        
        return DbToXmlResponse(
            success=True,
            message="모든 상품 데이터를 XML로 변환했습니다.",
            xml_file_path=str(xml_file_path),
            processed_count=total_count
        )
    except ValueError as e:
        logger.warning(f"DB to XML 변환 실패 (데이터 없음): {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"DB to XML 변환 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"DB to XML 변환 중 오류가 발생했습니다: {str(e)}")


@router.post("/by-gubun", response_model=DbToXmlResponse)
async def db_to_xml_by_gubun(request: DbToXmlByGubunRequest):
    """
    gubun(몰구분)별로 상품 데이터를 XML로 변환
    """
    try:
        xml_file_path = await ProductDbXmlService.db_to_xml_file_by_gubun(request.gubun)
        
        return DbToXmlResponse(
            success=True,
            message=f"gubun '{request.gubun}' 상품 데이터를 XML로 변환했습니다.",
            xml_file_path=str(xml_file_path)
        )
    except ValueError as e:
        logger.warning(f"DB to XML 변환 실패 (gubun: {request.gubun}): {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"DB to XML 변환 중 오류 (gubun: {request.gubun}): {e}")
        raise HTTPException(status_code=500, detail=f"DB to XML 변환 중 오류가 발생했습니다: {str(e)}")


@router.post("/by-ids", response_model=DbToXmlResponse)
async def db_to_xml_by_ids(request: DbToXmlByIdsRequest):
    """
    ID 리스트로 상품 데이터를 XML로 변환
    """
    try:
        xml_file_path = await ProductDbXmlService.db_to_xml_file_by_ids(request.ids)
        
        return DbToXmlResponse(
            success=True,
            message=f"ID {request.ids} 상품 데이터를 XML로 변환했습니다.",
            xml_file_path=str(xml_file_path),
            processed_count=len(request.ids)
        )
    except ValueError as e:
        logger.warning(f"DB to XML 변환 실패 (IDs: {request.ids}): {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"DB to XML 변환 중 오류 (IDs: {request.ids}): {e}")
        raise HTTPException(status_code=500, detail=f"DB to XML 변환 중 오류가 발생했습니다: {str(e)}")


@router.post("/by-product-name", response_model=DbToXmlResponse)
async def db_to_xml_by_product_name(request: DbToXmlByProductNmRequest):
    """
    상품명으로 상품 데이터를 XML로 변환 (부분 검색)
    """
    try:
        xml_file_path = await ProductDbXmlService.db_to_xml_file_by_product_nm(request.product_nm)
        
        return DbToXmlResponse(
            success=True,
            message=f"상품명 '{request.product_nm}' 상품 데이터를 XML로 변환했습니다.",
            xml_file_path=str(xml_file_path)
        )
    except ValueError as e:
        logger.warning(f"DB to XML 변환 실패 (상품명: {request.product_nm}): {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"DB to XML 변환 중 오류 (상품명: {request.product_nm}): {e}")
        raise HTTPException(status_code=500, detail=f"DB to XML 변환 중 오류가 발생했습니다: {str(e)}")


@router.post("/pagination", response_model=DbToXmlResponse)
async def db_to_xml_pagination(request: DbToXmlPaginationRequest):
    """
    페이징으로 상품 데이터를 XML로 변환
    """
    try:
        xml_file_path = await ProductDbXmlService.db_to_xml_file_pagination(request.skip, request.limit)
        
        return DbToXmlResponse(
            success=True,
            message=f"페이징(skip: {request.skip}, limit: {request.limit}) 상품 데이터를 XML로 변환했습니다.",
            xml_file_path=str(xml_file_path),
            processed_count=request.limit
        )
    except ValueError as e:
        logger.warning(f"DB to XML 변환 실패 (페이징 skip: {request.skip}, limit: {request.limit}): {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"DB to XML 변환 중 오류 (페이징 skip: {request.skip}, limit: {request.limit}): {e}")
        raise HTTPException(status_code=500, detail=f"DB to XML 변환 중 오류가 발생했습니다: {str(e)}")


@router.get("/count", response_model=ProductRawDataCountResponse)
async def get_product_raw_data_count():
    """
    test_product_raw_data 테이블의 총 상품 개수 조회
    """
    try:
        total_count = await ProductDbXmlService.get_product_raw_data_count()
        
        return ProductRawDataCountResponse(total_count=total_count)
    except Exception as e:
        logger.error(f"상품 개수 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"상품 개수 조회 중 오류가 발생했습니다: {str(e)}")


@router.get("/xml-string/all")
async def db_to_xml_string_all():
    """
    test_product_raw_data 테이블의 모든 데이터를 XML 문자열로 반환
    """
    try:
        xml_string = await ProductDbXmlService.db_to_xml_string_all()
        
        return {
            "success": True,
            "message": "모든 상품 데이터를 XML 문자열로 변환했습니다.",
            "xml_content": xml_string
        }
    except ValueError as e:
        logger.warning(f"DB to XML 변환 실패 (데이터 없음): {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"DB to XML 변환 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"DB to XML 변환 중 오류가 발생했습니다: {str(e)}") 