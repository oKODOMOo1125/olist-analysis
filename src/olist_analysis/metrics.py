import pandas as pd 

def summarize_by(df: pd.DataFrame, *cols: str, 
        value: str='delivery_days', min_n: int=30) -> pd.DataFrame:
    '''สรุปจำนวน และมัธยะฐานแยกตาม columns ที่ระบุตัดกลุ่มที่มีจำนวนเล็กกว่า 30'''
    out = (df.groupby(list(cols), observed=True)[value]
        .agg(n='size', n_notna='count', median='median')
        .reset_index())
    return out[out['n_notna'] >= min_n]