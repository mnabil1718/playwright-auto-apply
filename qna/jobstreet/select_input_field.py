from .input_field import InputField

class SelectInputField(InputField):
  def __init__(self, element, store):
    super().__init__(element, store)
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
    return self.locator.input_value() in ["", "Select an option"]
  
  def _print_available_options(self, option_texts):
      print(f"{self.label} (Choose an option):")
      for idx, opt in enumerate(option_texts, start=1):
          print(f"{idx} - {opt}")
     

  def answer(self):
    if self.store.is_key_exists(self.label):
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
