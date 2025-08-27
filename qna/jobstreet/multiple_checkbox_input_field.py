from .input_field import InputField

class MultipleCheckboxInputField(InputField):
    def __init__(self, element, store):
        super().__init__(element, store)

    @property
    def type(self):
        return "Multiple Checkboxes"

    @property
    def locator(self):
        # Only checkboxes, not radios
        return self.element.locator("input[type=checkbox]")
    
    # Override parent method because multiple checkbox is special
    def _extract_label_text(self) -> str:
        """
        Extract the question text for multi-checkbox blocks.
        Based on your DOM:
        div (container)
        ├─ div -> span -> span -> <strong> (question)
        └─ div -> checkboxes
        """
        strong_locator = self.element.locator("> div:first-of-type strong").first
        if strong_locator.count() > 0:
            return strong_locator.inner_text().strip()
        return "<Unknown multi-checkbox question>"

    def _get_options(self):
        opts = []
        for i in range(self.locator.count()):
            input_el = self.locator.nth(i)
            input_id = input_el.get_attribute("id")
            label_el = self.element.locator(f"label[for='{input_id}']")
            label_text = label_el.inner_text().strip()
            opts.append((input_el, label_text))
        return opts

    def _print_available_options(self, options):
        print(f"{self.label} (Choose one or more):")
        for idx, (_, label) in enumerate(options, start=1):
            print(f"{idx} - {label}")

    def is_empty(self) -> bool:
        for i in range(self.locator.count()):
            if self.locator.nth(i).is_checked():
                return False
        return True

    def answer(self):
        if self.store.is_key_exists(self.label):
            answers = self.store.get(self.label)
            if not isinstance(answers, list):
                answers = [answers]
        else:
            options = self._get_options()
            self._print_available_options(options)

            while True:
                raw = input("Enter numbers separated by commas: ").strip()
                try:
                    indices = [int(x) for x in raw.split(",") if x.strip().isdigit()]
                    answers = [options[i-1][1] for i in indices if 1 <= i <= len(options)]
                    if answers:
                        break
                    print("Please select at least one valid number.")
                except ValueError:
                    print("Invalid input. Please enter numbers separated by commas.")

            self.store.set(self.label, answers)

        # Actually click the chosen options
        for input_el, label_text in self._get_options():
            if label_text in answers:
                input_el.check()

    def clear_answer(self):
        if self.store.is_key_exists(self.label):
            self.store.pop(self.label)

        for i in range(self.locator.count()):
            if self.locator.nth(i).is_checked():
                self.locator.nth(i).uncheck()
