"""ล้างข้อมูล Olist: แปลงค่าให้ถูกชนิด และติดธงค่าที่เป็นไปไม่ได้"""

import math 

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

