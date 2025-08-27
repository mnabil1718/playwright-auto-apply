import re
from utils import SalaryRange
from typing import Tuple, Optional
from .input_field import InputField

class SalarySelectInputField(InputField):
  def __init__(self, element, store, salary_range_obj: SalaryRange):
    super().__init__(element, store)
    self.salary_range_obj = salary_range_obj
    self.opt_texts = self._generate_opt_texts(element)

  @property
  def type(self):
      return "Select"

  @property
  def locator(self):
      return self.element.locator("select") # specific children element, derived from parent
  
  @staticmethod
  def _generate_opt_texts(element):
    print("generating option labels...")
    locator = element.locator("select")
    options = locator.locator("option")
    return [options.nth(i).inner_text().strip() for i in range(1, options.count())]

  def is_empty(self) -> bool:
    answer = self.locator.input_value()

    if self.salary_range_obj:
      max_salary = self._select_max_possible_salary(self.opt_texts) 
      return answer != max_salary or answer in ["", "Select an option"]
    
    return answer in ["", "Select an option"]

  
  def _print_available_options(self, option_texts):
      print(f"{self.label} (Choose an option):")
      for idx, opt in enumerate(option_texts, start=1):
          print(f"{idx} - {opt}")

  @staticmethod
  def _parse_salary_option(text: str) -> Tuple[Optional[int], str]:
      """
      Parse salary option text into (value_in_idr, original_label, is_open_ended).

      Examples:
        "Rp 6 Jt"            -> (6000000, "Rp 6 Jt")
        "Rp 4.5 Jt"          -> (4500000, "Rp 4.5 Jt")
        "Rp 100 Jt atau lebih" -> (100000000, "Rp 100 Jt atau lebih")
      """
      
      # find something like "4.5" or "100"
      match = re.search(r"([\d,.]+)", text)
      if not match:
          return None, text

      num = float(match.group(1).replace(",", "."))
      value = int(num * 1_000_000)  # Jt = juta = million

      return value, text
  
  def _select_max_possible_salary(self, option_texts: list[str]) -> str:
      max_val = 0
      max_opt = ""

      print("Calculating max allowed salary...")
      for opt in option_texts:
        if opt in ["", "Select an option"]:
           continue
        
        val, txt = self._parse_salary_option(opt)
        if self.salary_range_obj.low <= val and self.salary_range_obj.high >= val:
            if val > max_val:
              max_val = val
              max_opt = txt
      
      return max_opt     

  def answer(self):
    if self.store.is_key_exists(self.label):
      if self.salary_range_obj:
        max_salary_opt = self._select_max_possible_salary(self.opt_texts)
        if self.store.get(self.label) != max_salary_opt:
          self.store.set(self.label, max_salary_opt)
      
        answer = max_salary_opt
      
      else:
        answer = self.store.get(self.label)

    else:
      self._print_available_options(self.opt_texts)
      
      # Ask user to pick a number
      while True:
          try:
              choice = int(input("Choose a number: "))
              if 1 <= choice <= len(self.opt_texts):
                  answer = self.opt_texts[choice - 1]
                  break
              
              else:
                  print(f"Please enter a number between 1 and {len(self.opt_texts)}.")

          except ValueError:
              print("Invalid input. Please enter a number.")
      
      self.store.set(self.label, answer)

    self.locator.select_option(label=answer)

  def clear_answer(self):
      if self.store.is_key_exists(self.label):
          self.store.pop(self.label)
    
      self.locator.select_option(index=0)
