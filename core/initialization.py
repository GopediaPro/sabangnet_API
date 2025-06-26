import os

def create_required_dirs():
    required_dirs = [
        "files/json",
        "files/xml",
        "files/xml/template",
        "files/logs",
        "files/xlsx"
    ]
    for d in required_dirs:
        os.makedirs(d, exist_ok=True)


# 프로그램 초기화 함수
def initialize_program():
    create_required_dirs()