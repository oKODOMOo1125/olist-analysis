"""กราฟที่ใช้ในรายงาน"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def one_star_by_days_late(df: pd.DataFrame, path: Path,
                          lo: int = -5, hi: int = 10, min_n: int = 30) -> pd.DataFrame:
    """อัตรา 1 ดาวต่อจำนวนวันที่เลยวันสัญญา บันทึกเป็น PNG แล้วคืนตารางที่ใช้วาด"""
    d = df[df["days_late"].between(lo, hi)]
    t = (d.groupby("days_late")
           .agg(n=("order_id", "size"),
                one_star_rate=("review_score", lambda x: (x == 1).mean()))
           .reset_index())
    t = t[t["n"] >= min_n]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(t["days_late"], t["one_star_rate"] * 100, marker="o")
    ax.axvline(0.5, linestyle="--", color="grey")
    ax.text(0.7, 5, "promised date passed", color="grey")
    ax.set_xlabel("Days after the promised date (negative = arrived early)")
    ax.set_ylabel("1-star reviews (%)")
    ax.set_title("1-star reviews jump on the first day a delivery is late")
    ax.set_ylim(0, None)
    fig.tight_layout()
    fig.savefig(path, dpi=150, metadata={"Software": None})
    plt.close(fig)
    return t