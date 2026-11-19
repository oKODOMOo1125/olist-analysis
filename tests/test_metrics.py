from olist_analysis import metrics
import pandas as pd
import pytest

def test_rates_by_state():
    df = pd.DataFrame({
        "order_id":       ["o1", "o2", "o3", "o4"],
        "customer_state": ["SP", "SP", "SP", "AM"],
        "delivery_days":  [5.0, 10.0, 30.0, 40.0],
        "days_late":      [-3, 2, 5, -10],
        "review_score":   [5, 1, 1, 4],
    })
    out = metrics.rates_by(df, "customer_state", slow_cutoff=20, min_n=1).set_index("customer_state")

    assert out.loc["SP", "n"] == 3
    assert out.loc["SP", "slow_rate"] == pytest.approx(1/3)
    assert out.loc["SP", "late_rate"] == pytest.approx(2/3)
    assert out.loc["SP", "one_star_rate"] == pytest.approx(2/3)
    assert out.loc["AM", "slow_rate"] == 1.0