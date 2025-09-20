#!/usr/bin/env python3
"""
ProductTextProcessor 단위 테스트 실행 스크립트
"""

import sys
import os
import subprocess

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.append(project_root)


def run_tests():
    """테스트 실행"""
    test_file = os.path.join(os.path.dirname(__file__), 'test_product_text_processor.py')
    
    print("ProductTextProcessor 단위 테스트 실행 중...")
    print(f"테스트 파일: {test_file}")
    print("-" * 50)
    
    try:
        # pytest로 테스트 실행
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            test_file, 
            '-v',  # 상세 출력
            '--tb=short',  # 짧은 traceback
            '--color=yes'  # 컬러 출력
        ], cwd=project_root, capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ 모든 테스트가 성공적으로 통과했습니다!")
        else:
            print(f"\n❌ 일부 테스트가 실패했습니다. (종료 코드: {result.returncode})")
            
        return result.returncode
        
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {str(e)}")
        return 1


def run_specific_test(test_name=None):
    """특정 테스트만 실행"""
    test_file = os.path.join(os.path.dirname(__file__), 'test_product_text_processor.py')
    
    cmd = [sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short', '--color=yes']
    
    if test_name:
        cmd.extend(['-k', test_name])
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {str(e)}")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ProductTextProcessor 테스트 실행')
    parser.add_argument('--test', '-t', help='특정 테스트만 실행 (테스트 이름 또는 패턴)')
    
    args = parser.parse_args()
    
    if args.test:
        print(f"특정 테스트 실행: {args.test}")
        exit_code = run_specific_test(args.test)
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)
