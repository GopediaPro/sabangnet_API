<img width="663" height="538" alt="image" src="https://github.com/user-attachments/assets/b8bbf393-484a-479b-81ae-23caa79786b3" /><img width="782" height="246" alt="image" src="https://github.com/user-attachments/assets/ba49a0d3-a6e6-4632-85a8-4145d6869819" />테스트 
    ~/project/sabangnet_API/test_macro/cmp.py

엑셀 파일 1개에 파이선시트[시트1, 시트2, 시트3], 매크로 시트[시트1_m, 시트2_m, 시트3_m) 순서로 엑셀 통합(시트 선택한 다음 시트복사 하시면 됩니다.)
시트 복사 방법
    1. 복사할 원천 엑셀과 대상 엑셀을 실행해서 함께 열어둡니다.
      <img width="1551" height="727" alt="image" src="https://github.com/user-attachments/assets/959ba2af-2484-4c00-886c-0a9190e6c55e" />
    2. 원천엑셀의 복사할 시트를 선택합니다. Ctrl을 누른 상태로 시트의 이름을 선택하면 한꺼번에 여러 시트를 선택할 수 있습니다.
       <img width="645" height="275" alt="image" src="https://github.com/user-attachments/assets/2416bf5f-a639-4cbb-9add-aea135d39375" />
    3. 선택한 시트를 오른쪽 클립합니다.
      <img width="463" height="382" alt="image" src="https://github.com/user-attachments/assets/d055510d-ff00-4381-8647-00cdcfbbb38b" />
    4. 메뉴에서 이동/복사 선택
    5. 통합대상문서 선택
    6. 끝으로 이동 선택
    7. 복사본 만들기 선택
    8. 확인 => 여기까지 완료하면 시트가 복사된 것을 확인할 수 있습니다.

엑셀이 없으면 리브레오피스를 사용하셔도 됩니다. 엑셀은 소스를 선택해서 대상에 붙여넣기 방식이지만 리브레는 현재 파일에 대상파일을 읽어오는 방식입니다.
    1. 복사본을 가진 파일을 열어둔다.  ex) libreoffice target.xlsx
    2. 메뉴 시트(S) > 파일에서 시트 삽입
      <img width="538" height="500" alt="image" src="https://github.com/user-attachments/assets/d63416a2-f87f-4ef4-a942-b8ca88929d45" />
    3. 읽어올 파일 선택 => 열기
      <img width="782" height="246" alt="image" src="https://github.com/user-attachments/assets/42eda275-0579-45e1-abf0-0f263ffffd4c" />
    4. 현재 시트 뒤에 선택
       <img width="669" height="540" alt="image" src="https://github.com/user-attachments/assets/ceb76acb-e012-4fb5-87ab-57bdf840f756" />
    5. 아래쪽의 파일에서 작성에서 읽어올 시트 선택(shift를 사용하면 여러개 선택 가능)
       <img width="663" height="538" alt="image" src="https://github.com/user-attachments/assets/18f1a210-cf91-4f75-aa36-7a1dfa6c449c" />
    6. 확인하면  => 여기까지 완료하면 시트가 복사된 것을 확인할 수 있습니다.

cmp.py 수정한 다음 사용하시면 되십니다.
  Line 182 : excel_file : 확인할 파일명
  Line 183 : compare_selected_sheet_pairs의  2번째 파라미터 (비교할 시트쌍의 개수)

실행:
  python cmp.py
