from abc import ABC, abstractmethod

class StoreInterface(ABC):
  """
  Provides encapsulated access to underlying 
  dictionary-like store interface. used for
  class as context manager.
  """

  @abstractmethod
  def is_key_exists(self, key) -> bool:
    pass
  
  @abstractmethod
  def set(self, key, value):
    pass
  
  @abstractmethod
  def get(self, key, default):
    pass
  
  @abstractmethod
  def pop(self, key):
    pass

  @abstractmethod
  def __enter__(self):
    """Enter context manager"""
    pass

  @abstractmethod
  def __exit__(self, exc_type, exc_val, exc_tb):
    """Exit context manager"""
    pass
  
  @abstractmethod
  def sync(self):
    pass