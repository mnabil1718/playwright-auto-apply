import re
from dataclasses import dataclass

@dataclass
class SalaryRange:
    low: int
    high: int

def parse_salary_range_idr(salary_text: str) -> SalaryRange:
    # Normalize
    cleaned = (
        salary_text.replace("Rp", "")
                   .replace("\xa0", " ")
                   .replace("per bulan", "")
                   .replace("per month", "")
                   .strip()
    )

    # Match numbers with . or , as separators
    nums = re.findall(r"\d[\d.,]*", cleaned)
    if not nums:
        return SalaryRange(0, 0)

    values = [int(n.replace(".", "").replace(",", "")) for n in nums]

    if "–" in cleaned or "-" in cleaned:
        low, high = values[0], values[1]
    else:
        low = high = values[0]

    print(low, high)
    return SalaryRange(low, high)


def format_min_salary(min_salary: int, labels: list[int]) -> str:
    """
    Translate min salary number in config into available filter label
    8000000 -> 8 Jt
    6000000 -> 6 Jt
    """

    if min_salary > max(labels):
        return f"{min_salary // 1_000_000} Jt +"

    for label in labels:
        if min_salary <= label:
            return f"{label // 1_000_000} Jt"
        
    return f"Rp. 0"



