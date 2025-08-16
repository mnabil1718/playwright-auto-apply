import shelve
from .store_interface import StoreInterface

class ShelveStore(StoreInterface):
  """
  Shelve store concrete class. 
  
  Use to manage access to underlying shelve file. Should 
  always be used as context manager. writeback attribute
  defaults to False.

  Attributes
    path (str): Specify where shelve .db file is located
    writeback (bool): control cache of all entries accessed, then writes back to
                      the dict at sync and close time. Use with caution as it can
                      consume much more memory.
  """

  def __init__(self, path: str, writeback: bool = False):
    self.path = path
    self._store = None
    self.writeback = writeback

  def __enter__(self):
    self._store = shelve.open(self.path, flag='c', writeback=self.writeback)
    return self
  
  def __exit__(self, exc_type, exc_val, exc_tb):
    # if hold cache via writeback=True, sync first then close
    if self._store and self.writeback and hasattr(self._store, 'sync'):
      self._store.sync()

    self._store.close()

  def sync(self):
    if hasattr(self._store, 'sync'):
      self._store.sync()

  def get(self, key, default=None):
    return self._store.get(key, default)
  
  def set(self, key, value):
    self._store[key] = value

  def is_key_exists(self, key) -> bool:
    return key in self._store
  
  def pop(self, key):
    return self._store.pop(key)

  

