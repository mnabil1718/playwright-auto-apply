import os, re
from utils import human_delay

class JobstreetAutomation:
  def __init__(self, config, browser, store):
    self.config = config
    self.browser = browser
    self.store = store
    self.page = None
    self.context = None

  def init(self):
    print("initializing app...")
    if os.path.exists(self.config["auth"]["storage_path"]):
      self.context = self.browser.new_context(storage_state=self.config["auth"]["storage_path"])
    else:
      self.context = self.browser.new_context()
    
    self.page = self.context.new_page()

  def auth(self):
    self.page.goto("https://id.jobstreet.com")
    self.page.get_by_role("main").get_by_role("link", name=re.compile("Masuk")).click()

    self.page.get_by_role("textbox", name=re.compile("Alamat email")).fill(self.config["auth"]["email"]) 
    self.page.get_by_role("button", name=re.compile("Kirimkan saya kode masuk")).click()

    while True:
      code = input("Enter 6-digit verification code: ")

      if not re.fullmatch(r"\d{6}", code):
        print("Code must be 6-digit numbers")
        continue


      self.page.get_by_role("textbox", name=re.compile("verification input")).fill(code) 

      self.page.wait_for_timeout(5000)

      if self.page.get_by_text(re.compile("Kode tidak valid. Coba lagi")).count() < 1:
        self.context.storage_state(path=self.config["auth"]["storage_path"])
        break


  def run(self):
      actions = [
        lambda: self.page.goto("https://id.jobstreet.com/?icmpid=js_global_landing_page")
      ]

      if not os.path.exists(self.config["auth"]["storage_path"]):
        self.auth()
        
      for action in actions:
        human_delay(self.page)
        action()
      
      self.browser.close()

