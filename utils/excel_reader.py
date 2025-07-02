from utils.sabangnet_path_utils import SabangNetPathUtils
from pathlib import Path
from typing import Optional

import pandas as pd


class ExcelReader:
    # 지원하는 파일 확장자들의 우선순위 (높은 순서부터)
    SUPPORTED_EXTENSIONS = ['.xlsx', '.xlsm', '.xls', '.csv']
    
    @staticmethod
    def read_excel_file(file_name: str, sheet_name: str) -> pd.DataFrame | str:
        """
        엑셀 파일을 읽어서 DataFrame으로 반환합니다.
        
        Args:
            file_name: 파일명 (확장자 포함/미포함 모두 가능)
            sheet_name: 시트명
            
        Returns:
            pd.DataFrame: 읽어온 데이터프레임
            
        Raises:
            FileNotFoundError: 파일을 찾을 수 없는 경우
        """
        excel_directory = SabangNetPathUtils.get_excel_file_path()
        target_file_path = ExcelReader._find_target_file(excel_directory, file_name)
        
        if not target_file_path.exists():
            raise FileNotFoundError(f"해당 파일을 찾을 수 없습니다. (파일명: {file_name})")
        
        # 파일 확장자에 따라 적절한 pandas 함수 사용
        df: pd.DataFrame = ExcelReader._read_file_by_extension(target_file_path, sheet_name)
        return df.fillna("")
    
    @staticmethod
    def _find_target_file(directory: Path, file_name: str) -> Path:
        """
        디렉토리에서 파일명에 해당하는 파일을 찾습니다.
        
        Args:
            directory: 검색할 디렉토리
            file_name: 찾을 파일명
            
        Returns:
            Path: 찾은 파일의 경로
        """
        # 파일명에 이미 확장자가 있는 경우
        if '.' in file_name and any(file_name.lower().endswith(ext) for ext in ExcelReader.SUPPORTED_EXTENSIONS):
            return directory / file_name
        
        # 확장자가 없는 경우 - 폴더에서 해당 파일명을 가진 파일들을 찾기
        base_name = Path(file_name).stem  # 확장자 제거
        
        # 우선순위에 따라 파일 찾기
        for extension in ExcelReader.SUPPORTED_EXTENSIONS:
            candidate_file = directory / f"{base_name}{extension}"
            if candidate_file.exists():
                return candidate_file
        
        # 정확히 일치하는 파일이 없으면 유사한 파일들 찾기
        similar_files = ExcelReader._find_similar_files(directory, base_name)
        if similar_files:
            # 첫 번째로 찾은 파일 반환 (우선순위 순서)
            return similar_files[0]
        
        # 아무것도 찾지 못한 경우 원래 파일명 반환 (에러 발생용)
        return directory / f"{base_name}.xlsx"
    
    @staticmethod
    def _find_similar_files(directory: Path, base_name: str) -> list[Path]:
        """
        디렉토리에서 base_name과 유사한 파일들을 찾습니다.
        
        Args:
            directory: 검색할 디렉토리
            base_name: 기본 파일명
            
        Returns:
            list[Path]: 찾은 파일들의 경로 리스트 (우선순위 순)
        """
        if not directory.exists():
            return []
        
        similar_files = []
        
        # 지원하는 확장자로 끝나는 모든 파일들 검사
        for file_path in directory.iterdir():
            if file_path.is_file():
                file_stem = file_path.stem.lower()
                file_ext = file_path.suffix.lower()
                
                if (file_ext in ExcelReader.SUPPORTED_EXTENSIONS and 
                    base_name.lower() in file_stem):
                    similar_files.append(file_path)
        
        # 확장자 우선순위에 따라 정렬
        similar_files.sort(key=lambda x: ExcelReader.SUPPORTED_EXTENSIONS.index(x.suffix.lower()) 
                          if x.suffix.lower() in ExcelReader.SUPPORTED_EXTENSIONS else 999)
        
        return similar_files
    
    @staticmethod
    def _read_file_by_extension(file_path: Path, sheet_name: str) -> pd.DataFrame:
        """
        파일 확장자에 따라 적절한 pandas 함수로 파일을 읽습니다.
        
        Args:
            file_path: 읽을 파일 경로
            sheet_name: 시트명

        Returns:
            pd.DataFrame: 읽어온 데이터프레임
        """
        extension = file_path.suffix.lower()
        
        if extension in ['.xlsx', '.xlsm', '.xls']:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        elif extension == '.csv':
            return pd.read_csv(file_path, sheet_name=sheet_name, encoding='utf-8-sig')  # 한글 지원
        else:
            # 기본적으로 엑셀로 시도
            return pd.read_excel(file_path, sheet_name=sheet_name)
    
    @staticmethod
    def list_available_files() -> list[str] | str:
        """
        사용 가능한 엑셀 파일들의 목록을 반환합니다.
        
        Returns:
            list[str]: 파일명 리스트
        """
        excel_directory = SabangNetPathUtils.get_excel_file_path()
        
        if not excel_directory.exists():
            return "엑셀 파일이 없습니다."
        
        available_files = []
        for file_path in excel_directory.iterdir():
            if (file_path.is_file() and file_path.suffix.lower() in ExcelReader.SUPPORTED_EXTENSIONS):
                available_files.append(file_path.name)
        
        return sorted(available_files)