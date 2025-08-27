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

    # Prefer <legend> or <strong> inside the container (the actual question text)
    strong_locator = self.element.locator("legend strong, div strong").first
    if strong_locator.count() > 0:
        return strong_locator.inner_text().strip()

    # If there's a legend without strong
    legend_locator = self.element.locator("legend").first
    if legend_locator.count() > 0:
        return legend_locator.inner_text().split("\n")[0].strip()

    # Fallback: take the first label text (single inputs)
    label_locator = self.element.locator("label").first
    if label_locator.count() > 0:
        return label_locator.inner_text().split("\n")[0].strip()

    return "<Unknown question>"


  def has_error(self):
    pass
  
  def is_optional(self):
    pass
  
  def retry_answer(self):
    pass
  
  @abstractmethod
  def is_empty(self):
    pass

  @abstractmethod
  def answer(self):
    pass
  
  @abstractmethod
  def clear_answer(self):
     pass
  
  
