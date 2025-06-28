import pandas as pd
from pathlib import Path
from models.base_model import Base


class ConvertXlsx:

    def translate_field(self, data: Base, mapping_field: dict):
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

    def export_translated_to_excel(self, data: list[dict], mapping_field: dict, file_name: str):
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
            self.translate_field(row, mapping_field) for row in data]
        df = pd.DataFrame(translated_data)

        file_path = Path('./files/xlsx')
        file_path.mkdir(exist_ok=True)

        full_path = file_path / f"{file_name}.xlsx"

        df.to_excel(full_path, index=False)
        return str(full_path)