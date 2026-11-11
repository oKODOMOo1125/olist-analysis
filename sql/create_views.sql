-- นิยามกลาง: ออเดอร์ที่ส่งถึงลูกค้าแล้ว ในขอบเขตรายงาน
-- ลำดับเมื่อโหลดข้อมูลใหม่:
--   1) DROP VIEW (บรรทัดแรกของไฟล์นี้)  2) scripts/load_to_postgres.py
--   3) sql/add_primary_key.sql           4) ไฟล์นี้ทั้งไฟล์

DROP VIEW IF EXISTS olist.delivered_v;

CREATE VIEW olist.delivered_v AS
WITH o AS (
    SELECT
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp::timestamp       AS purchased_at,
        order_delivered_carrier_date::timestamp   AS carrier_at,
        order_delivered_customer_date::timestamp  AS delivered_at,
        order_estimated_delivery_date::timestamp  AS estimated_at
    FROM olist.orders
)
SELECT
    order_id,
    customer_id,
    order_status,
    purchased_at,
    delivered_at,
    estimated_at,
    EXTRACT(EPOCH FROM (delivered_at - purchased_at)) / 86400  AS delivery_days,  -- เก็บชั่วโมงไว้ เหมือน .dt.total_seconds()/86400
    delivered_at::date - estimated_at::date                    AS days_late       -- นับเป็นวัน เหมือน .dt.normalize() แล้ว .dt.days
FROM o
WHERE delivered_at IS NOT NULL                                  -- ส่งถึงแล้วเท่านั้น
  AND purchased_at >= '2017-01-01' AND purchased_at < '2018-09-01'  -- ขอบเขตเดียวกับ ReportConfig
  AND delivered_at >= purchased_at                              -- ตัดวันที่ที่เป็นไปไม่ได้ (is_date_error)
  AND (carrier_at IS NULL OR delivered_at >= carrier_at);

-- เช็ก: จำนวนควรได้ 96,204 ลบด้วย date error ที่อยู่ในขอบเขต (ไม่เกิน 23)
-- SELECT COUNT(*) FROM olist.delivered_v;
