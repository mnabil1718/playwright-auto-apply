from abc import ABC, abstractmethod

class InputFieldInterface(ABC):
  @abstractmethod
  def is_empty(self) -> bool:
    pass
  
  @abstractmethod
  def set_answer(self, qna_dict):
    pass
  
  @abstractmethod
  def clear_answer(self, qna_dict):
    pass