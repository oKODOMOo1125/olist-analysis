-- รันหลัง scripts/load_to_postgres.py ทุกครั้ง
-- ถ้าคำสั่งไหน error แปลว่า grain ของตารางนั้นไม่เป็นอย่างที่คิด

alter table olist.orders  add primary key (order_id);
alter table olist.customer add primary key (customer_id);
alter table olist.order_items add primary key (order_id,order_item_id);
alter table olist.order_reviews  add primary key (review_id, order_id);