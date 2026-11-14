from olist_analysis import cleaning 
import pytest
import pandas as pd

def test_clean_price_remove_comma():
    assert cleaning.clean_price('1,250') == 1250.0

def test_clean_price_return_none():
    assert cleaning.clean_price('ไม่ทราบ') is None


@pytest.mark.parametrize(
    'days_late, expected',
    [
        (-3, 'on_time'),
        (0, 'on_time'),
        (1, 'late_1_7d'),
        (7, 'late_1_7d'),
        (8, 'late_8d_plus'),
        (None, 'unknown'),
        (float('nan'), 'unknown'),
    ],
)
def test_delivery_status(days_late, expected):
    assert cleaning.delivery_status(days_late) == expected


def make_orders() -> pd.DataFrame:
    """ตาราง orders จิ๋ว 3 แถว ที่คำนวณคำตอบด้วยมือได้"""
    return pd.DataFrame({
        "order_id": ["a", "b", "c"],
        "order_purchase_timestamp": pd.to_datetime(
            ["2018-01-01 23:00", "2018-01-01 10:00", "2018-01-01 10:00"]),
        "order_delivered_carrier_date": pd.to_datetime(
            ["2018-01-02", "2018-01-05", "2018-01-03"]),
        "order_delivered_customer_date": pd.to_datetime(
            ["2018-01-03 01:00", "2018-01-04 00:00", None]),
        "order_estimated_delivery_date": pd.to_datetime(
            ["2018-01-10", "2018-01-03", "2018-01-10"]),
    })

def test_clean_orders_keeps_hours():
    out = cleaning.clean_orders(make_orders())
    assert out.loc[0, 'delivery_days'] == pytest.approx(26/24)

def test_clean_orders_keeps_undelivered_as_missing():
    out = cleaning.clean_orders(make_orders())
    assert pd.isna(out.loc[2, 'delivery_days'])

def test_clean_orders_labels_and_flags():
    out = cleaning.clean_orders(make_orders())
    assert out['delivery_status'].to_list() == ["on_time", "late_1_7d", "unknown"]
    assert out['is_date_error'].to_list() == [False, True, False]

def test_clean_orders_does_not_change_input():
    out = make_orders()
    cleaning.clean_orders(out)
    assert 'delivery_day' not in out.columns

def test_require_columns_names_missing_column():
    with pytest.raises(KeyError, match='discount'):
        assert cleaning.require_columns(make_orders(), ['order_id', 'discount'])

def test_clean_price_brazil_format():
    assert cleaning.clean_price("1.250,00") == 1250.0

@pytest.mark.parametrize(
    "status, expected",
    [
        ("delivered", "delivered"),
        ("shipped", "in_progress"),
        ("created", "in_progress"),
        ("canceled", "failed"),
        ("unavailable", "failed"),
        ("lost_in_space", "unknown"),
    ],
)
def test_status_group(status, expected):
    assert cleaning.status_group(status) == expected