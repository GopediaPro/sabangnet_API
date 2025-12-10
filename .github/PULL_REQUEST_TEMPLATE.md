# -n 은 가장 최근 commit 개수 (push한 commit 개수) 
export COMMIT_LATEST=$(git rev-list --reverse dev..HEAD | tail -n 14 | head -n 1)
git diff $COMMIT_LATEST^..HEAD > changes.diff
git log $COMMIT_LATEST..HEAD -n 14 --pretty=format:"%h %s" --name-status > commit_summary.txt
git diff --stat $COMMIT_LATEST^..HEAD > changes_stat.txt

# PR prompt 입니다.
## 작성된 PR 자료를 Markdown 툴(obsidian,...)에 복사 붙여넣기 한 다음 다시 복사 github PR에 붙여넣기 해야함.

You are an expert software developer and technical writer. Your task is to refine a Pull Request (PR) template and then draft a PR description using that refined template, referencing provided file changes.

Here's the current PR template content:
"""
## 📋 프로세스 시각화
## 🎯 개요
## 🔄 변경 사항 (<details> <summary><strong>🔸 Repository 계층 개선</strong></summary></details> 활용)
## 🆕 주요 신규 * 변경 기능
## 🏗️ 아키텍처 개선사항
## 🔄 처리 플로우
## 🎯 관련 이슈
## 🔍 데이터 스키마 변경
## 🏆 기대 효과
## 📂 주요 변경 파일
"""

First, **review and improve the provided PR template** by:
1. Ensuring all necessary sections are present for a comprehensive PR.
2. Clarifying any ambiguous sections.
3. Suggesting additional explanations or guidance within the template for each section if needed, particularly for the "<details>" tag usage.
4. Identifying and removing any unnecessary or redundant explanations.

Second, **using the refined PR template, draft a PR description** based on the information that would typically be found in the following attached files (assume these files contain relevant content for a PR):
- `changes_stat.txt` (summary of file changes, lines added/deleted)
- `changes.diff` (detailed code differences)
- `commit_summary.txt` (commit messages and summaries)

The goal is to create a clear, concise, and highly effective PR template and then demonstrate its use by generating a comprehensive PR description that summarizes the changes from the provided files.

- refined PR template은 보여주지말고 바로 적용시켜서 PR 만들어줘.
- 적절한 PR 제목도 만들어줘.
- Endpoint & data schema 변경이 있으면 Front 쪽에서 API 연동하거나, 관리하기 편하도록 내용 추가로 정리해줘.
