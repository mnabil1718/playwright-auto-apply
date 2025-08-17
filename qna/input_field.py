from abc import ABC, abstractmethod

class InputField(ABC):
  def __init__(self, element, store):
    self.element = element
    self.label = self._extract_label_text()
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
  
  def _extract_label_text(self) -> str:
    """Parses the complex label element to find the clean question text."""
    label_element = self.element.locator("label, legend").first

    # Check for the primary, visible text container
    main_text_locator = label_element.locator("span[aria-hidden='true']").first

    if main_text_locator.count() > 0:
        return main_text_locator.inner_text().strip()
    
    # Fallback for other label structures
    full_text = label_element.inner_text()
    return full_text.split('\n')[0].strip()


  def has_error(self):
    return bool(self.element.locator(".artdeco-inline-feedback--error").count())
  
  def is_optional(self):
    return not self.element.locator("label[for], legend").count()
  
  def retry_answer(self):
    error_message = self.element.locator(".artdeco-inline-feedback__message").inner_text().strip()
    print(f"Error: {error_message}")
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
  
  
