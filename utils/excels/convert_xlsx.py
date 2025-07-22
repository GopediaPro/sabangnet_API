import pandas as pd
from pathlib import Path
from models.base_model import Base
import os


class ConvertXlsx:
    def export_translated_to_excel(self,
                                   data: list[Base],
                                   mapping_field: dict,
                                   file_name: str,
                                   file_path: str = './files/excel') -> str:
        """
        Translate the data to the Korean field name and save it as an Excel file.
        Args:
            data: SQLAlchemy ORM 인스턴스
            mapping_field: {한글필드명: 영문필드명} 
            file_name: 파일 이름
        Returns:
            Excel 파일 경로
        """
        translated_data: list[dict] = [
            self._translate_field(row, mapping_field) for row in data]
        df = pd.DataFrame(translated_data)

        file_path = Path(file_path)
        file_path.mkdir(exist_ok=True)

        full_path = file_path / f"{file_name}.xlsx"

        df.to_excel(full_path, index=False)
        return full_path, file_name

    def export_temp_excel(self,
                          data: list[Base],
                          mapping_field: dict,
                          file_name: str = None,
                          ) -> str:
        """
        export temp excel file
        Args:
            data: SQLAlchemy ORM 인스턴스
            mapping_field: {한글필드명: 영문필드명} 
            file_name: 파일 이름
        Returns:
            Excel 파일 경로
        """
        translated_data: list[dict] = [
            self._translate_field(row, mapping_field) for row in data]
        df = pd.DataFrame(translated_data)
        if not file_name.endswith(".xlsx"):
            file_name = f"{file_name}.xlsx"

        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)

        temp_file_path = os.path.join(temp_dir, file_name)

        df.to_excel(temp_file_path, index=False)
        return temp_file_path

    def _translate_field(self, data: Base, mapping_field: dict) -> dict:
        """
        Translate english key name to korean key name.
        Args:
            data: SQLAlchemy ORM 인스턴스
            mapping_field: {한글필드명: 영문필드명} 
        Returns:
            {한글필드명: 영문필드명} 
        """
        result = {}
        for key, value in mapping_field.items():
            if callable(value):
                result[key] = value(data)
            elif value:
                result[key] = getattr(data, value.lower(), None)
            else:
                result[key] = None
        return result
