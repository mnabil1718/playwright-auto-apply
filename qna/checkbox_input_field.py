from .input_field import InputField

class CheckboxInputField(InputField):
  def __init__(self, element, store):
    super().__init__(element, store)

  @property
  def type(self):
      return "Check box"

  @property
  def locator(self):
      return self.element.locator("input[type=checkbox], input[type=radio]")

  def is_empty(self) -> bool:
    for option in range(self.locator.count()):
      if self.locator.nth(option).is_checked():
        return False
      
    return True

  def answer(self):
    if self.store.is_key_exists(self.label):
      answer = self.store.get(self.label)

    else:
      answer = input(f"{self.label} (Yes/No): ").strip().capitalize()
      self.store.set(self.label, answer)

    self.element.get_by_text(answer, exact=True).click()

  def clear_answer(self):
      if self.store.is_key_exists(self.label):
          self.store.pop(self.label)
    
      for option in range(self.locator.count()):
          if self.locator.nth(option).is_checked():
              self.locator.nth(option).uncheck()
