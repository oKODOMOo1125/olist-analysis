from pathlib import Path
import pandas as pd

RAW_FILES = {
    "customer": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv" ,
    "category": "product_category_name_translation.csv"
}

DATE_COLUMNS = {
    "customer": [],
    "geolocation": [],
    "order_items": ['shipping_limit_date'],
    "order_payments": [],
    "order_reviews": ['review_creation_date','review_answer_timestamp'],
    "orders": ['order_purchase_timestamp','order_approved_at','order_delivered_carrier_date','order_delivered_customer_date','order_estimated_delivery_date'],
    "products": [],
    "sellers": [],
    "category": []
}

TEXT_COLUMNS = {
    "customer": ["customer_id","customer_unique_id","customer_zip_code_prefix","customer_city","customer_state"],
    "geolocation": ['geolocation_zip_code_prefix','geolocation_city','geolocation_state'],
    "order_items": ['order_id','product_id','seller_id'],
    "order_payments": ['order_id','payment_type	'],
    "order_reviews": ['review_id','order_id','review_comment_title','review_comment_message'],
    "orders": ['order_id','customer_id','order_status'],
    "products": ['product_id','product_category_name'],
    "sellers": ['seller_id','seller_zip_code_prefix','seller_city','seller_state'],
    "category": ['product_category_name','product_category_name_english']
}

INT_COLUMNS = {
    "customer": [],
    "geolocation": [],
    "order_items": [],
    "order_payments": [],
    "order_reviews": [],
    "orders": [],
    "products": ['product_name_lenght','product_description_lenght','product_photos_qty'],
    "sellers": [],
    "category": []
}


def read_table(name: str, raw_dir: Path) -> pd.DataFrame:
    '''อ่านไฟล์ CSV และแปลงชนิดข้อมูลตามที่กำหนดไว้'''
    file_path = Path(raw_dir) / RAW_FILES[name]
    dtype_01 = {col: 'string' for col in TEXT_COLUMNS[name]}
    dtype_02 = {col: 'Int64' for col in INT_COLUMNS[name]}
    dtype = {**dtype_01, **dtype_02}
    return pd.read_csv(file_path, dtype=dtype, parse_dates= DATE_COLUMNS[name])
    