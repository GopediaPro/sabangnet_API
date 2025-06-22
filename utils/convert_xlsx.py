import pandas as pd
from pathlib import Path


class ConvertXlsx:

    def translate_field(self, data: list[dict], mapping_field: dict):
        """
        Translate english key name to korean key name.
        """
        return {
            key: data.get(value.lower()) for key, value in mapping_field.items()
        }

    def export_translated_to_excel(self, data: list[dict], mapping_field: dict, file_name: str):
        """
        Translate the data to the Korean field name and save it as an Excel file.
        """
        translated_data: list[dict] = [
            self.translate_field(row, mapping_field) for row in data]
        df = pd.DataFrame(translated_data)

        file_path = Path('./files/xlsx')
        file_path.mkdir(exist_ok=True)

        full_path = file_path / f"{file_name}.xlsx"

        df.to_excel(full_path, index=False)
        return str(full_path)
