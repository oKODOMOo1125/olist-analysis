import pandas as pd 

def summarize_by(df: pd.DataFrame, *cols: str, 
        value: str='delivery_days', min_n: int=30) -> pd.DataFrame:
    '''สรุปจำนวน และมัธยะฐานแยกตาม columns ที่ระบุตัดกลุ่มที่มีจำนวนเล็กกว่า 30'''
    out = (df.groupby(list(cols), observed=True)[value]
        .agg(n='size', n_notna='count', median='median')
        .reset_index())
    return out[out['n_notna'] >= min_n]

def rates_by(df: pd.DataFrame, *group_cols: str,
             slow_cutoff: float, min_n: int = 30) -> pd.DataFrame:
    """สรุปต่อกลุ่ม: n, เวลาส่งมัธยฐาน, สัดส่วนช้าเกิน slow_cutoff,
    สัดส่วนเลยวันสัญญา, สัดส่วน 1 ดาว · ตัดกลุ่มที่ n < min_n"""
    out = (df.groupby(list(group_cols), observed=True)
             .agg(n=("order_id", "size"),
                  median_days=("delivery_days", "median"),
                  slow_rate=("delivery_days", lambda x: (x > slow_cutoff).mean()),
                  late_rate=("is_late", "mean"),
                  one_star_rate=("review_score", lambda x: (x == 1).mean()))
             .reset_index())
    return out[out["n"] >= min_n]