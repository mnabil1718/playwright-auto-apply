import re
from utils import SalaryRange
from typing import Tuple, Optional
from .input_field import InputField

class SalarySelectInputField(InputField):
  def __init__(self, element, store, config, salary_range_obj: SalaryRange):
    super().__init__(element, store)
    self.salary_range_obj = salary_range_obj
    self.config = config
    self.opt_texts = self._generate_opt_texts(element)

  @property
  def type(self):
      return "Select"

  @property
  def locator(self):
      return self.element.locator("select") # specific children element, derived from parent
  
  # make options into class attribute
  # because salary select does not have
  # empty value and there's always default
  # salary value selected
  @staticmethod
  def _generate_opt_texts(element):
    print("generating salary option labels...")
    locator = element.locator("select")
    options = locator.locator("option")
    return [options.nth(i).inner_text().strip() for i in range(1, options.count())]

  def is_empty(self) -> bool:
    input_val = self.locator.input_value()
    answer = self.locator.locator(f"option[value='{input_val}']").inner_text()
    curr_salary, _ = self._parse_salary_option(answer)
    # if selection is not min salary, consider empty
    if self._is_salary_not_min(curr_salary):
       return True
    
    if self.salary_range_obj:
      return answer != self._select_max_possible_salary(self.opt_texts) 
    
    return answer in ["", "Select an option"]
  
  def _is_salary_not_min(self, salary: int) -> bool:
      if salary != self.config["search"].get("min_salary", 7000000):
        return True
      
      return False
     
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
        val, txt = self._parse_salary_option(opt)
        if self.salary_range_obj.low <= val and self.salary_range_obj.high >= val:
            if val > max_val:
              max_val = val
              max_opt = txt
      
      return max_opt  

  def _generate_valid_options(self) -> list[str]:
      opts = []
      for opt in self.opt_texts:        
        val, txt = self._parse_salary_option(opt)
        if self.salary_range_obj.low <= val and self.salary_range_obj.high >= val:
           opts.append(txt)

      return opts
              

  def answer(self):
      answer = None

      if not self.salary_range_obj:
        if self.store.is_key_exists(self.label):
              answer = self.store.get(self.label)
        else:
            self._print_available_options(self.opt_texts)
            while True:
                try:
                    choice = int(input("Choose a number: "))
                    if 1 <= choice <= len(self.opt_texts):
                        answer = self.opt_texts[choice - 1]
                        self.store.set(self.label, answer)
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(self.opt_texts)}.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

      else:
          # Always prefer max salary if range is available
          max_salary_opt = self._select_max_possible_salary(self.opt_texts)
          stored = self.store.get(self.label) if self.store.is_key_exists(self.label) else None

          # Use stored if already equal, otherwise overwrite with max salary
          if stored != max_salary_opt:
              self.store.set(self.label, max_salary_opt)
          answer = max_salary_opt
          
      print("Salary Picked:", answer)
      self.locator.select_option(label=answer)


  def clear_answer(self):
      if self.store.is_key_exists(self.label):
          self.store.pop(self.label)
    
      self.locator.select_option(index=0)
