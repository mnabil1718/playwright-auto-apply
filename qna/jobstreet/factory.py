from .multiple_checkbox_input_field import MultipleCheckboxInputField
from .radio_input_field import RadioInputField
from .select_input_field import SelectInputField
from .salary_select_input_field import SalarySelectInputField
from utils import SalaryRange

def input_field_factory(element, store, config, salary_range_obj: SalaryRange = None):
    """
    factory method to init child class by element type
    """
    checkboxes = element.locator("input[type='checkbox']")
    radios = element.locator("input[type='radio']")
    selects = element.locator("select")

    if checkboxes.count():
        return MultipleCheckboxInputField(element, store)
    
    elif radios.count():
        return RadioInputField(element, store)
    
    elif selects.count():
        label = element.locator("label, legend").first.inner_text().strip().lower()

        salary_keywords = [
            "expected monthly basic salary",   # English
            "gaji bulanan yang kamu inginkan"  # Indonesian
        ]
        if any(kw in label for kw in salary_keywords):
            return SalarySelectInputField(element, store, config, salary_range_obj)
        
        return SelectInputField(element, store)

    print(f"Unknown answer type: {element.locator('label, legend').first.inner_text().strip()}")
    return None