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
    text = str(value).strip().replace(',','' ).replace('฿','').replace('บาท','').strip()
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
    if days_late <= 0:
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


def clean_order_dates(df:pd.DataFrame)->pd.DataFrame:
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

