"""
โหลด ตารางข้อมูล Olist ลงใน PostgreSQL ใน schema ชื่อ olist

ก่อนรัน set -a; scource .env; set +a เพิ่อนำ DATABASE_URL จากไฟล์ .env มาใช้ได้
รัน uv run python Scripts/load_to postgre.py
"""

import os
from pathlib import Path 
from sqlalchemy import create_engine, text
from olist_analysis import load 

raw_dir =Path('data/raw/olist')
SCHEMA = 'olist'

def main() -> None:
    ''''โหลดข้อมูล olist ลงใน PostgreSQL'''
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise SystemExit('ต้องรัน -a; scource .env; set +a เพิ่อนำ DATABASE_URL จากไฟล์ .env ก่อน')
    
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA}'))

    for name in load.RAW_FILES:
        df = load.read_table(name, raw_dir)
        df.to_sql(name, engine,schema=SCHEMA, if_exists='replace',
                   index=False , chunksize= 10_000)
        print(f"{name:15s} {len(df):>9,} ROW -> {SCHEMA}.{name}")

if __name__ == "__main__" :
    main()
