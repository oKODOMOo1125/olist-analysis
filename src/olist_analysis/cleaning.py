# เครื่องมือสำหรับ clean colunm เกี่ยวกับราคาให้ เป็น float ทั้งหมด 

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

