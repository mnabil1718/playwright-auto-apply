from .single_text_input_field import SingleTextInputField
from .textarea_input_field import TextAreaInputField
from .checkbox_input_field import CheckboxInputField
from .select_input_field import SelectInputField

def input_field_factory(element, store):
    """
    factory method to init child class by element type
    """
    if element.locator("textarea").count():
      return TextAreaInputField(element, store)
    elif element.locator("input[type='text']").count():
      return SingleTextInputField(element, store)
    elif element.locator("fieldset").count():
      return CheckboxInputField(element, store)
    elif element.locator("select").count():
      return SelectInputField(element, store)
    else:
      print(f"Skipping unknown answer type for question: {element.locator('label, legend').first.inner_text().strip()}")
      return None