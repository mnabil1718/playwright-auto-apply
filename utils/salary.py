import re
from dataclasses import dataclass

# dataclass works like Struct in other languages
@dataclass
class SalaryRange:
    """
    Represents salary range. if single-value salary, low and high is the same.
    """
    low: int
    high: int

def parse_salary_range_idr(salary_text: str) -> SalaryRange:
    # Remove Rp, dots, non-breaking spaces etc.
    cleaned = salary_text.replace("Rp", "").replace(".", "").replace("\xa0", " ")
    # Extract all numbers
    nums = re.findall(r"\d+", cleaned)
    if not nums:
        return SalaryRange(0, 0)
    
    if "–" in cleaned or "-" in cleaned:
        # Range case
        low, high = int(nums[0]), int(nums[1])
    else:
        # Single value case (e.g. "Rp 10.000.000 per month")
        low = high = int(nums[0])
    
    return SalaryRange(low, high)