"""ตรวจคุณภาพข้อมูล: แต่ละ check ตอบคำถามเดียว ว่ามีกี่แถวที่ผิดกติกา"""
from dataclasses import dataclass

import pandas as pd

BRAZIL_STATES = {
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
}


@dataclass(frozen=True)
class CheckResult:
    name: str
    n_bad: int
    passed: bool


class Check:
    """แม่แบบ: ลูกทุกตัวต้องเขียน bad_rows ของตัวเอง ส่วน run ใช้ร่วมกัน"""
    name = "check"

    def bad_rows(self, df: pd.DataFrame) -> pd.Series:
        raise NotImplementedError(f"{type(self).__name__} ยังไม่ได้เขียน bad_rows")

    def run(self, df: pd.DataFrame) -> CheckResult:
        n_bad = int(self.bad_rows(df).sum())
        return CheckResult(name=self.name, n_bad=n_bad, passed=(n_bad == 0))


# ---------- ค่าว่าง / ซ้ำ ----------

class NotNull(Check):
    def __init__(self, column: str):
        self.column = column
        self.name = f"not_null({column})"

    def bad_rows(self, df):
        return df[self.column].isna()


class Unique(Check):
    def __init__(self, *columns: str):
        self.columns = list(columns)
        self.name = f"unique({', '.join(columns)})"

    def bad_rows(self, df):
        return df.duplicated(subset=self.columns, keep=False)


class NotBlank(Check):
    def __init__(self, column: str):
        self.column = column
        self.name = f"not_blank({column})"

    def bad_rows(self, df):
        return df[self.column].str.strip() == ""


# ---------- ค่าอยู่ในขอบเขต (ค่าว่างไม่นับ เป็นงานของ NotNull) ----------

class NotNegative(Check):
    def __init__(self, column: str):
        self.column = column
        self.name = f"not_negative({column})"

    def bad_rows(self, df):
        return df[self.column] < 0


class InRange(Check):
    def __init__(self, column: str, low, high):
        self.column = column
        self.low = low
        self.high = high
        self.name = f"in_range({column}, {low}–{high})"

    def bad_rows(self, df):
        col = df[self.column]
        return col.notna() & ~col.between(self.low, self.high)


class HasLength(Check):
    def __init__(self, column: str, length: int):
        self.column = column
        self.length = length
        self.name = f"has_length({column}, {length})"

    def bad_rows(self, df):
        col = df[self.column]
        return col.notna() & (col.str.len() != self.length)


class AllowedValues(Check):
    def __init__(self, column: str, allowed):
        self.column = column
        self.allowed = set(allowed)
        self.name = f"allowed_values({column})"

    def bad_rows(self, df):
        col = df[self.column]
        return col.notna() & ~col.isin(self.allowed)


# ---------- ความสัมพันธ์ระหว่างคอลัมน์ / ตาราง ----------

class DateOrder(Check):
    def __init__(self, earlier: str, later: str):
        self.earlier = earlier
        self.later = later
        self.name = f"date_order({earlier} <= {later})"

    def bad_rows(self, df):
        return df[self.later] < df[self.earlier]   # มีค่าว่างฝั่งไหน ผลเป็น False เอง


class ExistsIn(Check):
    def __init__(self, column: str, ref_table: pd.DataFrame, ref_column: str):
        self.column = column
        self.ref_table = ref_table
        self.ref_column = ref_column
        self.name = f"exists_in({column} -> {ref_column})"

    def bad_rows(self, df):
        col = df[self.column]
        return col.notna() & ~col.isin(self.ref_table[self.ref_column])


def run_checks(df: pd.DataFrame, tests: list[Check]) -> pd.DataFrame:
    """รันทุก check แล้วคืนตาราง 1 แถวต่อ 1 check"""
    return pd.DataFrame([t.run(df) for t in tests])
