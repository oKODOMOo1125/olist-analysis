"""ล้างข้อมูล Olist: แปลงค่าให้ถูกชนิด และติดธงค่าที่เป็นไปไม่ได้"""

import math 
import pandas as pd

def clean_price(value:object) -> float|None:
    # เครื่องมือสำหรับ clean colunm เกี่ยวกับราคาให้ เป็น float ทั้งหมด 
    if value == None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return None if math.isnan(value) else float(value)
    text = str(value).strip().replace('฿','').replace('บาท','').strip()
    if ',' in text and '.' in text:
        if text.rfind(',') > text.rfind('.'):
            text = text.replace('.','').replace(',','.')
        else: 
            text = text.replace(',','')
    else:
        text = text.replace(',','')

    if text == '':
        return None 
    try:
        return float(text)
    except ValueError:
        return None


def delivery_status(days_late: float|None) -> str:
    """ ติดป้ายสถานะการส่งจากจำนวนวันที่ช้า

    >>> delivery_status(-3)
    'on_time'
    >>> delivery_status(None)
    'unknown'
    """
    if days_late is None or math.isnan(days_late):
        return 'unknown'
    if days_late < 0:
        return  'on_time'
    elif  days_late <=7:
        return  'late_1_7d'
    else:
        return 'late_8d_plus'


def require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    """หยุดทันทีถ้า df ขาดคอลัมน์ที่ต้องใช้ และบอกชื่อทุกตัวที่ขาด"""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f'missing columns: {missing}')


def clean_orders(df:pd.DataFrame)->pd.DataFrame:
    """เพิ่มคอลัมน์เวลาส่งให้ตาราง orders โดย 1 แถว = 1 ออเดอร์ เหมือนเดิม"""
    require_columns(df, [
        'order_purchase_timestamp',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ])
    out = df.copy()

    purchas = out['order_purchase_timestamp']
    carrier = out['order_delivered_carrier_date']
    delivered = out['order_delivered_customer_date']
    estimated = out['order_estimated_delivery_date']

    out['delivery_days'] = (delivered - purchas).dt.total_seconds() /86400
    out['days_late'] = (delivered.dt.normalize() - estimated).dt.days
    out['delivery_status'] = out['days_late'].map(delivery_status)
    out['is_date_error'] = (delivered < purchas)| (delivered < carrier)

    return out


def status_group(value):
    match value:
        case 'delivered':
            return 'delivered'
        case 'created' | 'approved' | 'invoiced' | 'processing' | 'shipped':
            return 'in_progress'
        case 'canceled' | 'unavailable':
            return 'failed'
        case _:
            return 'unknown'

def latest_reviews(review: pd.DataFrame) -> pd.DataFrame:
    '''กรองให้เหลือแต่ review ล่าสุดต่อออเดอร์เท่านั้น'''
    return (review
            .sort_values('review_answer_timestamp')
            .drop_duplicates('order_id', keep='last')
    
)

def build_order_table(orders: pd.DataFrame, reviews: pd.DataFrame,
                      customers: pd.DataFrame, start: str, end: str
                      ) -> tuple[pd.DataFrame, pd.Series]:
    """รวม orders + รีวิวล่าสุด + รัฐลูกค้า แล้วกรองตามขอบเขต
    คืน (ตาราง 1 แถว = 1 ออเดอร์ที่ส่งถึงและมีรีวิว, จำนวนแถวที่เหลือแต่ละขั้น)"""
    merged = (clean_orders(orders)
              .merge(latest_reviews(reviews)[["order_id", "review_score"]],
                     on="order_id", how="left", validate="one_to_one")
              .merge(customers[["customer_id", "customer_unique_id", "customer_state"]],
                     on="customer_id", how="left", validate="one_to_one"))

    steps = {"orders ทั้งหมด": len(merged)}
    s = merged[merged["order_purchase_timestamp"].between(start, end, inclusive="left")]
    steps["สั่งในช่วงขอบเขต"] = len(s)
    s = s[s["delivery_days"].notna()]
    steps["ส่งถึงลูกค้าแล้ว"] = len(s)
    s = s[~s["is_date_error"]]
    steps["วันที่เป็นไปได้"] = len(s)
    s = s[s["review_score"].notna()]
    steps["มีรีวิว"] = len(s)

    return s.reset_index(drop=True), pd.Series(steps, name="n")