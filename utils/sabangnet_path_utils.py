from pathlib import Path


class SabangNetPathUtils:

    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    @classmethod
    def get_project_root(cls) -> Path:
        return cls.PROJECT_ROOT

    @classmethod
    def get_files_path(cls) -> Path:
        return cls.PROJECT_ROOT / "files"

    @classmethod
    def get_xlsx_file_path(cls) -> Path:
        return cls.get_files_path() / "xlsx"

    @classmethod
    def get_xml_file_path(cls) -> Path:
        return cls.get_files_path() / "xml"

    @classmethod
    def get_xml_template_path(cls) -> Path:
        return cls.get_xml_file_path() / "templates"
