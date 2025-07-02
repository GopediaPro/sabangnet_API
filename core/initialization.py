import os

def create_required_dirs():
    required_dirs = [
        "files/json",
        "files/xml",
        "files/xml/templates",
        "files/logs",
        "files/excel"
    ]
    for d in required_dirs:
        os.makedirs(d, exist_ok=True)


# 프로그램 초기화 함수
def initialize_program():
    create_required_dirs()