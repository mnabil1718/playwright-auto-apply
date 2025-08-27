from .input_field import InputField

class RadioInputField(InputField):
    def __init__(self, element, store):
        super().__init__(element, store)

    @property
    def type(self):
        return "radio box"

    @property
    def locator(self):
        # Works for both radio & checkbox inputs
        return self.element.locator("input[type=radio]")

    def _get_options(self):
        """Return [(value, label), ...] for all options"""
        opts = []
        for i in range(self.locator.count()):
            input_el = self.locator.nth(i)
            # Get text from the label tied to this input
            input_id = input_el.get_attribute("id")
            label_el = self.element.locator(f"label[for='{input_id}']")
            label_text = label_el.inner_text().strip()
            opts.append((input_el, label_text))
        return opts

    def _print_available_options(self, options):
        print(f"{self.label} (Choose an option):")
        for idx, (_, label) in enumerate(options, start=1):
            print(f"{idx} - {label}")

    def is_empty(self) -> bool:
        for i in range(self.locator.count()):
            if self.locator.nth(i).is_checked():
                return False
        return True

    def answer(self):
        if self.store.is_key_exists(self.label):
            answer = self.store.get(self.label)
        else:
            options = self._get_options()
            self._print_available_options(options)

            while True:
                try:
                    choice = int(input("Choose a number: "))
                    if 1 <= choice <= len(options):
                        _, answer = options[choice - 1]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(options)}.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

            self.store.set(self.label, answer)

        # Actually click the option
        for input_el, label_text in self._get_options():
            if label_text == answer:
                input_el.check()
                break

    def clear_answer(self):
        if self.store.is_key_exists(self.label):
            self.store.pop(self.label)

        for i in range(self.locator.count()):
            if self.locator.nth(i).is_checked():
                self.locator.nth(i).uncheck()
