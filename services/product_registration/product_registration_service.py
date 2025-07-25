"""
Product Registration Service
상품 등록 비즈니스 로직 처리 서비스
"""

from typing import List, Optional, Tuple
from utils.logs.sabangnet_logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

from repository.product_registration_repository import ProductRegistrationRepository
from utils.excels.excel_processor import ProductRegistrationExcelProcessor
from schemas.product_registration import (
    ProductRegistrationCreateDto, 
    ProductRegistrationResponseDto,
    ProductRegistrationBulkResponseDto,
    ExcelProcessResultDto
)


logger = get_logger(__name__)


class ProductRegistrationService:
    """상품 등록 비즈니스 로직 서비스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ProductRegistrationRepository(session)
        self.excel_processor = ProductRegistrationExcelProcessor()
    
    async def process_excel_file(self, file_path: str, sheet_name: str = "Sheet1") -> ExcelProcessResultDto:
        """
        Excel 파일을 처리하여 상품 등록 데이터를 추출합니다.
        
        Args:
            file_path: Excel 파일 경로
            sheet_name: 시트명
            
        Returns:
            ExcelProcessResultDto: Excel 처리 결과
        """
        try:
            logger.info(f"Excel 파일 처리 시작: {file_path}")
            
            # Excel 데이터 읽기
            raw_data = self.excel_processor.read_excel_k_to_az_columns(file_path, sheet_name)
            
            # 데이터 검증
            valid_data, validation_errors = self.excel_processor.validate_data(raw_data)
            
            # DTO로 변환
            processed_data = []
            for data_item in valid_data:
                try:
                    dto = ProductRegistrationCreateDto(**data_item)
                    processed_data.append(dto)
                except Exception as e:
                    logger.warning(f"DTO 변환 실패: {e}")
                    validation_errors.append(f"DTO 변환 오류: {str(e)}")
            
            result = ExcelProcessResultDto(
                total_rows=len(raw_data),
                valid_rows=len(processed_data),
                invalid_rows=len(raw_data) - len(processed_data),
                validation_errors=validation_errors,
                processed_data=processed_data
            )
            
            logger.info(f"Excel 처리 완료: 총 {result.total_rows}행, 유효 {result.valid_rows}행")
            return result
            
        except Exception as e:
            logger.error(f"Excel 파일 처리 오류: {e}")
            raise
    
    async def create_single_product(self, data: ProductRegistrationCreateDto) -> ProductRegistrationResponseDto:
        """
        단일 상품 등록 데이터를 생성합니다.
        
        Args:
            data: 생성할 데이터 DTO
            
        Returns:
            ProductRegistrationResponseDto: 생성된 데이터 응답 DTO
        """
        try:
            logger.info("단일 상품 등록 데이터 생성 시작")
            
            # 데이터 생성
            created_data = await self.repository.create_single(data)
            await self.session.commit()
            
            # 응답 DTO로 변환
            response_dto = ProductRegistrationResponseDto.from_orm(created_data)
            
            logger.info(f"단일 상품 등록 완료: ID={created_data.id}")
            return response_dto
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"단일 상품 등록 오류: {e}")
            raise
    
    async def create_bulk_products(self, data_list: List[ProductRegistrationCreateDto]) -> ProductRegistrationBulkResponseDto:
        """
        대량 상품 등록 데이터를 생성합니다.
        
        Args:
            data_list: 생성할 데이터 DTO 리스트
            
        Returns:
            ProductRegistrationBulkResponseDto: 대량 생성 결과 응답 DTO
        """
        try:
            logger.info(f"대량 상품 등록 시작: {len(data_list)}개")
            
            created_ids = []
            success_data = []
            errors = []
            
            # 배치 단위로 처리 (성능 최적화)
            batch_size = 100
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                
                try:
                    # 배치 단위 생성
                    batch_ids = await self.repository.create_bulk(batch)
                    created_ids.extend(batch_ids)
                    
                    # 생성된 데이터 조회 (응답용)
                    for id in batch_ids:
                        created_item = await self.repository.get_by_id(id)
                        if created_item:
                            success_data.append(ProductRegistrationResponseDto.from_orm(created_item))
                    
                except Exception as e:
                    error_msg = f"배치 {i//batch_size + 1} 처리 오류: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            await self.session.commit()
            
            # 결과 응답 생성
            response = ProductRegistrationBulkResponseDto(
                success_count=len(created_ids),
                error_count=len(data_list) - len(created_ids),
                created_ids=created_ids,
                errors=errors,
                success_data=success_data
            )
            
            logger.info(f"대량 상품 등록 완료: 성공 {response.success_count}개, 실패 {response.error_count}개")
            return response
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"대량 상품 등록 오류: {e}")
            raise
    
    async def process_excel_and_create(self, file_path: str, sheet_name: str = "Sheet1") -> Tuple[ExcelProcessResultDto, ProductRegistrationBulkResponseDto]:
        """
        Excel 파일을 처리하고 바로 DB에 저장합니다.
        
        Args:
            file_path: Excel 파일 경로
            sheet_name: 시트명
            
        Returns:
            Tuple[ExcelProcessResultDto, ProductRegistrationBulkResponseDto]: 
            Excel 처리 결과와 DB 저장 결과
        """
        try:
            logger.info(f"Excel 파일 처리 및 DB 저장 시작: {file_path}")
            
            # 1. Excel 파일 처리
            excel_result = await self.process_excel_file(file_path, sheet_name)
            
            if not excel_result.processed_data:
                logger.warning("처리할 유효한 데이터가 없습니다.")
                empty_bulk_result = ProductRegistrationBulkResponseDto(
                    success_count=0,
                    error_count=0,
                    created_ids=[],
                    errors=["처리할 유효한 데이터가 없습니다."],
                    success_data=[]
                )
                return excel_result, empty_bulk_result
            
            # 2. DB에 저장
            bulk_result = await self.create_bulk_products(excel_result.processed_data)
            
            logger.info(f"Excel 파일 처리 및 DB 저장 완료")
            return excel_result, bulk_result
            
        except Exception as e:
            logger.error(f"Excel 파일 처리 및 DB 저장 오류: {e}")
            raise
    
    async def get_product_by_id(self, id: int) -> Optional[ProductRegistrationResponseDto]:
        """
        ID로 상품 등록 데이터를 조회합니다.
        
        Args:
            id: 조회할 데이터 ID
            
        Returns:
            Optional[ProductRegistrationResponseDto]: 조회된 데이터 또는 None
        """
        try:
            data = await self.repository.get_by_id(id)
            if data:
                return ProductRegistrationResponseDto.from_orm(data)
            return None
            
        except Exception as e:
            logger.error(f"상품 조회 오류: {e}")
            raise
    
    async def get_products_list(self, limit: int = 100, offset: int = 0) -> List[ProductRegistrationResponseDto]:
        """
        상품 등록 데이터 목록을 조회합니다.
        
        Args:
            limit: 조회할 데이터 수 제한
            offset: 조회 시작 위치
            
        Returns:
            List[ProductRegistrationResponseDto]: 조회된 데이터 리스트
        """
        try:
            data_list = await self.repository.get_all(limit, offset)
            return [ProductRegistrationResponseDto.from_orm(data) for data in data_list]
            
        except Exception as e:
            logger.error(f"상품 목록 조회 오류: {e}")
            raise
    
    async def search_products(self, search_term: str, limit: int = 50) -> List[ProductRegistrationResponseDto]:
        """
        상품명으로 데이터를 검색합니다.
        
        Args:
            search_term: 검색어
            limit: 조회할 데이터 수 제한
            
        Returns:
            List[ProductRegistrationResponseDto]: 검색된 데이터 리스트
        """
        try:
            data_list = await self.repository.search_by_name(search_term, limit)
            return [ProductRegistrationResponseDto.from_orm(data) for data in data_list]
            
        except Exception as e:
            logger.error(f"상품 검색 오류: {e}")
            raise
    
    async def update_product(self, id: int, data: ProductRegistrationCreateDto) -> Optional[ProductRegistrationResponseDto]:
        """
        상품 등록 데이터를 업데이트합니다.
        
        Args:
            id: 업데이트할 데이터 ID
            data: 업데이트할 데이터 DTO
            
        Returns:
            Optional[ProductRegistrationResponseDto]: 업데이트된 데이터 또는 None
        """
        try:
            updated_data = await self.repository.update_by_id(id, data)
            await self.session.commit()
            
            if updated_data:
                return ProductRegistrationResponseDto.from_orm(updated_data)
            return None
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"상품 업데이트 오류: {e}")
            raise
    
    async def delete_product(self, id: int) -> bool:
        """
        상품 등록 데이터를 삭제합니다.
        
        Args:
            id: 삭제할 데이터 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            deleted = await self.repository.delete_by_id(id)
            await self.session.commit()
            
            return deleted
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"상품 삭제 오류: {e}")
            raise
