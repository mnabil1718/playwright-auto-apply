from .input_field import InputField

class SingleTextInputField(InputField):
  def __init__(self, element, store):
    super().__init__(element, store)

  @property
  def type(self):
      return "Single text"

  @property
  def locator(self):
      return self.element.locator("input[type='text']") # specific children element, derived from parent
  

  def is_empty(self) -> bool:
    return not self.locator.input_value().strip()

  def answer(self):
    if self.store.is_key_exists(self.label):
      answer = self.store.get()
    else:
      answer = input(f"{self.label}: ")
      self.store.set(self.label, answer)

    self.locator.fill(answer)

  def clear_answer(self):
    if self.store.is_key_exists(self.label):
      self.store.pop(self.label)
    
    self.locator.fill("")
