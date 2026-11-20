from pathlib import Path 
from olist_analysis import checks, cleaning, load, metrics
from olist_analysis.config import ReportConfig, PROJECT_ROOT

REPORTS = PROJECT_ROOT / 'reports'

VALID_STATUS = ["created", "approved", "invoiced", "processing",
                "shipped", "delivered", "canceled", "unavailable"]

def main():
    cfg = ReportConfig()
    REPORTS.mkdir(exist_ok=True)

    #1.โหลด ตราราง orders reviews customers
    orders = load.read_table('orders', cfg.raw_dir)
    reviews = load.read_table('order_reviews', cfg.raw_dir)
    customers = load.read_table('customer', cfg.raw_dir)

    #2.ตรวจสอบคุณภาพข้อมูล
    orders_quality = checks.run_checks(orders, [
        checks.Unique('order_id'),
                    checks.NotNull('order_delivered_customer_date'),
                    checks.DateOrder('order_purchase_timestamp', 'order_delivered_customer_date'),
                    checks.DateOrder('order_delivered_carrier_date', 'order_delivered_customer_date'),
                    checks.DateOrder("order_purchase_timestamp", "order_delivered_carrier_date"),
                    checks.AllowedValues('order_status', VALID_STATUS)
    ])

    reviews_quality = checks.run_checks(reviews, [
                    checks.Unique('review_id','order_id'),
                    checks.Unique('order_id'),
                    checks.InRange('review_score', 1, 5)
    ])

    #3.ทำความสะอาดข้อมูล

    df, funnel = cleaning.build_order_table(orders, reviews, customers, cfg.start, cfg.end)
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)

    #4.สำรวจข้อมูล 
    p90 = df['delivery_days'].quantile(0.9)

    state_by = metrics.rates_by(df, 'customer_state',slow_cutoff=p90, min_n=cfg.min_n).sort_values('late_rate', ascending=False)

    month_rate = metrics.rates_by(df, 'month',slow_cutoff=p90, min_n=cfg.min_n).sort_values('late_rate', ascending=False)

    #5 สร้างรายงาน
    orders_quality.to_csv(REPORTS / 'order_quality_check.csv', index=False)
    reviews_quality.to_csv(REPORTS / 'review_quality_check.csv', index=False)
    funnel.to_csv(REPORTS / 'funnel.csv', header=True)
    state_by.round(4).to_csv(REPORTS / 'rate_by_state.csv', index=False)
    month_rate.round(4).to_csv(REPORTS / 'rate_by_month.csv', index=False)

    q = df['delivery_days'].quantile([0.25, 0.5, 0.75, 0.9])

    summary = (
        'สรุปผล (Olist)\n\n'
        f'- จำนวนออเดอร์ที่ใช้วิเคราะห์ทั้งหมด {len(df):,} ออเดอร์ โดยอยู่ในช่วง {cfg.start} ถึงก่อน {cfg.end} โดยจะเป็นออเดอร์ที่ส่งถึงแล้วทั้งหมดและมีรีวิว\n'
        f'- ระยะเวลาส่ง median {q[0.5]:.1f} วัน โดยมี IQR อยู่ในช่วง {q[0.25]:.1f} - {q[0.75]:.1f} วัน และ P90 {q[0.9]:.1f} (10% รอนานกว่านี้)\n'
        f'- โดยอัตราการส่งเกินกำหนดของทั้งประเทศคิดเป็น {(df["days_late"] > 0).mean():.1%} อัตราได้ 1 ดาว ทั้งประเทศคิดเป็น {(df["review_score"] == 1).mean():.1%}\n'
     )

    (REPORTS / 'summary.md').write_text(summary, encoding='utf-8')
    print(f'เขียนรายงานลง {REPORTS} แล้ว ( n = {len(df):,}')


if __name__ == "__main__":
        main()





