git diff main..HEAD > changes.diff
git log main..HEAD --pretty=format:"%h %s" --name-status > commit_summary.txt
git diff --stat main..HEAD > changes_stat.txt

첨부된 파일과 """## 📋 프로세스 시각화 ## 🎯 개요 ## 🔄 변경 사항 (<details> <summary><strong>🔸 Repository 계층 개선</strong></summary></details> 활용) ## 🆕 주요 신규 * 변경 기능 ## 🏗️ 아키텍처 개선사항 ## 🔄 처리 플로우 ## 🎯 관련 이슈 ## 🔍 데이터 스키마 변경 ## 🏆 기대 효과 ## 📂 주요 변경 파일""" PR template 참고해서 PR 작성해줘.

작성된 PR 자료를 Markdown 툴(obsidian,...)에 복사 붙여넣기 한 다음 다시 복사 github PR에 붙여넣기 해야함.
