import pandas as pd

from olist_analysis import checks


def test_allowed_values_ignores_null():
    df = pd.DataFrame({"state": ["SP", "XX", "RJ", None, "sp"]})
    result = checks.AllowedValues("state", checks.BRAZIL_STATES).run(df)
    assert result.n_bad == 2          # "XX" กับ "sp" ส่วน None ไม่นับ
    assert result.passed is False


def test_in_range_ignores_null():
    df = pd.DataFrame({"score": [1, 5, 6, None]})
    assert checks.InRange("score", 1, 5).run(df).n_bad == 1   # มีแค่ 6


def test_has_length_ignores_null():
    df = pd.DataFrame({"zip": ["01310", "123", None]})
    assert checks.HasLength("zip", 5).run(df).n_bad == 1


def test_unique_counts_every_copy():
    df = pd.DataFrame({"order_id": ["a", "a", "b"]})
    assert checks.Unique("order_id").run(df).n_bad == 2      # keep=False นับทุกตัวที่ซ้ำ


def test_date_order():
    df = pd.DataFrame({
        "bought": pd.to_datetime(["2018-01-01", "2018-01-05", "2018-01-01"]),
        "arrived": pd.to_datetime(["2018-01-03", "2018-01-02", None]),
    })
    assert checks.DateOrder("bought", "arrived").run(df).n_bad == 1


def test_exists_in():
    customers = pd.DataFrame({"customer_id": ["c1", "c2"]})
    orders = pd.DataFrame({"customer_id": ["c1", "c9", None]})
    assert checks.ExistsIn("customer_id", customers, "customer_id").run(orders).n_bad == 1


def test_run_checks_one_row_per_check():
    df = pd.DataFrame({"state": ["SP", "XX", None]})
    report = checks.run_checks(df, [
        checks.NotNull("state"),
        checks.AllowedValues("state", checks.BRAZIL_STATES),
    ])
    assert report["n_bad"].tolist() == [1, 1]
    assert list(report.columns) == ["name", "n_bad", "passed"]
