import pandas as pd
from typing import List, Optional, Any


def create_hanjin_print_records_dataframe(
    created_records: List[Any], 
    batch_id: Optional[str] = None
) -> pd.DataFrame:
    """
    한진 프린트 서비스의 생성된 레코드들을 DataFrame으로 변환합니다.
    
    Args:
        created_records: 생성된 레코드들의 리스트
        batch_id: 배치 ID (선택사항)
        
    Returns:
        pd.DataFrame: 변환된 DataFrame
    """
    df_data = []
    
    for record in created_records:
        # created_at의 timezone 정보 제거
        created_at_str = None
        if record.created_at:
            if hasattr(record.created_at, 'replace'):
                # timezone 정보 제거
                created_at_naive = record.created_at.replace(tzinfo=None)
                created_at_str = created_at_naive.strftime('%Y-%m-%d %H:%M:%S')
            else:
                created_at_str = str(record.created_at)
        
        df_data.append({
            'batch_id': batch_id,
            'idx': record.idx,
            'msg_key': record.msg_key,
            'result_code': record.result_code,
            'result_message': record.result_message,
            'wbl_num': record.wbl_num,
            'prt_add': record.prt_add,
            'zip_cod': record.zip_cod,
            'snd_zip': record.snd_zip,
            'created_at': created_at_str
        })
    
    return pd.DataFrame(df_data)
