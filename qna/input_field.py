from abc import ABC, abstractmethod

class InputField(ABC):
  def __init__(self, element, store):
    self.element = element
    self.label = element.locator("label, legend").first.inner_text().strip()
    self.store = store

  @property
  @abstractmethod
  def type(self):
      """Child classes must implement type attribute"""
      pass
  
  @property
  @abstractmethod
  def locator(self):
      """Child classes must implement locator attribute"""
      pass

  def has_error(self):
    return bool(self.element.locator(".artdeco-inline-feedback--error").count())
  
  def is_optional(self):
    return not self.element.locator("label[for], legend").count()
  
  def retry_answer(self):
    error_message = self.element.locator(".artdeco-inline-feedback__message").inner_text().strip()
    print(f"Error for {self.label}: {error_message}")
    self.answer()
  
  @abstractmethod
  def is_empty(self):
    pass

  @abstractmethod
  def answer(self):
    pass
  
  @abstractmethod
  def clear_answer(self):
     pass
  
  
