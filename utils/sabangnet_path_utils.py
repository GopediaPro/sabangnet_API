from pathlib import Path


class SabangNetPathUtils:
    """
    경로 찾아주는 클래스이고 `Path(__file__).resolve().parent.parent` 라서 파일 위치 바뀌면 안됨.
    """

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
    def get_log_file_path(cls) -> Path:
        return cls.get_files_path() / "logs"
    
    @classmethod
    def get_xml_template_path(cls) -> Path:
        return cls.get_xml_file_path() / "templates"
