from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class ReportConfig:
    '''ค่าตั้งของรายงาน
     raw_dir: โฟลเดอร์ไฟล์ CSV ของ Olist (เทียบกับโฟลเดอร์โปรเจกต์)
    start, end: ใช้ออเดอร์ที่สั่งตั้งแต่ start ถึงก่อน end
    min_n: ไม่รายงานกลุ่มที่มีค่าจริงน้อยกว่านี้
    '''
    raw_dir: Path = PROJECT_ROOT/ 'data/raw/olist'
    start: str = "2017-01-01"
    end: str = "2018-09-01"
    min_n: int = 30

