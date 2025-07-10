import os
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
        # root/files/
        os.makedirs(cls.PROJECT_ROOT / "files", exist_ok=True)
        return cls.PROJECT_ROOT / "files"

    @classmethod
    def get_json_file_path(cls) -> Path:
        # root/files/json/
        os.makedirs(cls.get_files_path() / "json", exist_ok=True)
        return cls.get_files_path() / "json"

    @classmethod
    def get_excel_file_path(cls) -> Path:
        # root/files/excel/
        os.makedirs(cls.get_files_path() / "excel", exist_ok=True)
        return cls.get_files_path() / "excel"

    @classmethod
    def get_xml_file_path(cls) -> Path:
        # root/files/xml/
        os.makedirs(cls.get_files_path() / "xml", exist_ok=True)
        return cls.get_files_path() / "xml"

    @classmethod
    def get_log_file_path(cls) -> Path:
        # root/files/logs/
        os.makedirs(cls.get_files_path() / "logs", exist_ok=True)
        return cls.get_files_path() / "logs"
    
    @classmethod
    def get_xml_template_path(cls) -> Path:
        # root/files/xml/templates/
        os.makedirs(cls.get_xml_file_path() / "templates", exist_ok=True)
        return cls.get_xml_file_path() / "templates"

    @classmethod
    def get_xml_request_path(cls) -> Path:
        # root/files/xml/request/
        os.makedirs(cls.get_xml_file_path() / "request", exist_ok=True)
        return cls.get_xml_file_path() / "request"
    
    @classmethod
    def get_xml_response_path(cls) -> Path:
        # root/files/xml/response/
        os.makedirs(cls.get_xml_file_path() / "response", exist_ok=True)
        return cls.get_xml_file_path() / "response"
    