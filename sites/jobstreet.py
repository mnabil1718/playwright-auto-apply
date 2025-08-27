import os, re
from utils import human_delay, parse_salary_range_idr, SalaryRange
from qna.jobstreet import input_field_factory
from playwright.sync_api import expect

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

  def search_position_and_location(self):
    self.page.get_by_role('combobox', name=re.compile("Pekerjaan apa?")).fill(self.config["search"].get("position", "Backend Developer"))

    # IT job positions
    self.page.get_by_text(re.compile("Tampilkan daftar klasifikasi")).click(force=True)
    self.page.get_by_test_id("6281").click()
    # self.page.get_by_test_id("6283").click()
    # self.page.get_by_test_id("6286").click()
    # self.page.get_by_test_id("6287").click()
    # self.page.get_by_test_id("6289").click()
    # self.page.get_by_test_id("6290").click()
    # self.page.get_by_test_id("6291").click()
    # self.page.get_by_test_id("6294").click()
    # self.page.get_by_test_id("6295").click()
    # self.page.get_by_test_id("6297").click()
    # self.page.get_by_test_id("6299").click()
    # self.page.get_by_test_id("6301").click()
    # self.page.get_by_test_id("6302").click()
    # self.page.get_by_test_id("6303").click()
    self.page.get_by_text(re.compile("Tampilkan daftar klasifikasi")).click(force=True)

    self.page.get_by_role('combobox', name=re.compile("Di mana?")).fill(self.config["search"].get("location", "Indonesia"))

  def job_type_filter(self):
    self.page.locator("label").filter(has_text=re.compile("Tampilkan filter jenis")).locator("svg").click()
    self.page.get_by_role("checkbox", name="Full time").click()
    self.page.get_by_role("checkbox", name="Kontrak/Temporer").click()
    self.page.get_by_role("checkbox", name="Paruh waktu").click()
    self.page.get_by_role("checkbox", name="Kasual/Liburan").click()

  def remote_filter(self):
    self.page.locator("label").filter(has_text=re.compile("Tampilkan filter work")).locator('svg').click()
    self.page.get_by_role("checkbox", name=re.compile("Kantor")).click()
    self.page.get_by_role("checkbox", name=re.compile("Hibrid")).click()
    self.page.get_by_role("checkbox", name=re.compile("Jarak jauh")).click()
    self.page.locator("label").filter(has_text=re.compile("Tampilkan filter work")).locator('svg').click(force=True)

  def min_salary(self):
    self.page.locator("label").filter(has_text=re.compile("Tampilkan filter gaji minimum")).locator("svg").click()
    self.page.get_by_role("radio", name="6 jt").click()

  def time_range_filter(self):
    self.page.locator("label").filter(has_text="Tampilkan filter tanggal").locator('svg').click()
    self.page.get_by_role("radio", name=re.compile("7 hari terakhir")).click()

  def _company_filter_match(self, company_name: str):
    blacklist = self.config["search"].get("company_blacklist", [])
    for company in blacklist:
      if company.casefold() in company_name.casefold():
          return True
    
    return False

  def answer_questions(self, new_tab, salary_range_obj: SalaryRange = None):
    continue_btn = new_tab.get_by_test_id("continue-button")
    submit_btn = new_tab.get_by_test_id('review-submit-application')

    new_tab.wait_for_load_state()

    # Step 1 - cover letter
    new_tab.get_by_test_id("coverLetter-method-none").check()
    continue_btn = new_tab.get_by_test_id("continue-button")
    expect(continue_btn).to_be_enabled(timeout=10000)
    continue_btn.click()
    human_delay(new_tab)

    # Step 2 - loop until career history page
    while True:
        if new_tab.locator('div[data-automation="career-history-section"]').count():
          break
        
        new_tab.wait_for_selector("form > div", timeout=10000)
        questions = new_tab.locator("form > div > *")
        total_children = questions.count()

        # At least 1 child must exist (nav buttons)
        if total_children <= 1:
            break

        count = total_children - 1  # exclude nav section
        print(f"Found {count} questions.")

        for i in range(count):
            print(f"Processing question #{i + 1}...")
            q = questions.nth(i)
            field = input_field_factory(q, self.store, salary_range_obj)
            human_delay(new_tab)

            if field.is_empty():
                field.answer()

        # Ensure the button is ready before clicking
        continue_btn = new_tab.get_by_test_id("continue-button")
        expect(continue_btn).to_be_enabled(timeout=10000)
        continue_btn.click()
        human_delay(new_tab)

    # Step 3 - career history page
    continue_btn = new_tab.get_by_test_id("continue-button")
    expect(continue_btn).to_be_enabled(timeout=10000)
    continue_btn.click()
    human_delay(new_tab)

    # Step 4 - submit
    submit_btn = new_tab.get_by_test_id("review-submit-application")
    submit_btn.scroll_into_view_if_needed()
    expect(submit_btn).to_be_enabled(timeout=10000)
    submit_btn.click()
    human_delay(new_tab, 1500, 4000)

  def _extract_salary_range(self, new_tab) -> SalaryRange | None:
    salary_el = new_tab.locator('[data-automation="job-detail-salary"]')
    if salary_el.count():
        salary_text = salary_el.inner_text()
        return parse_salary_range_idr(salary_text)
    
    return None
     

  def apply_jobs(self):
      job_limit = self.config["search"].get("job_limit", 3)

      # Wait for job cards
      self.page.wait_for_selector("article[data-testid='job-card']", timeout=15000)
      job_items = self.page.locator("article[data-testid='job-card']")
      limit = min(job_limit, job_items.count())

      for i in range(limit):
        job = job_items.nth(i)

        # Click job to open details
        job.click()
        human_delay(self.page)

        # Company name scoped inside this job card
        company_locator = job.locator("a[data-automation='jobCompany']")
        quick_apply_btn = self.page.get_by_role("link").filter(has_text="Lamaran Cepat")

        if company_locator.count():
            company_name = company_locator.first.inner_text().strip()
            if self._company_filter_match(company_name):
                print(f"Skipped {company_name}. Blacklisted")
                continue
            
            
            if not quick_apply_btn.count():
              print(f"Skipped {company_name}. No easy apply")
              continue

            with self.page.expect_popup() as popup_info:
              quick_apply_btn.click()

            new_tab = popup_info.value

            salary_range_obj = self._extract_salary_range(new_tab)
            self.answer_questions(new_tab, salary_range_obj)
            new_tab.close()
            
        print(f"Applied job #{i + 1}")


  def run(self):
      actions = [
        lambda: self.page.goto("https://id.jobstreet.com/?icmpid=js_global_landing_page"),
        lambda: self.search_position_and_location(),
        lambda: self.job_type_filter(),
        lambda: self.remote_filter(),
        lambda: self.remote_filter(),
        lambda: self.min_salary(),
        lambda: self.time_range_filter(),
        lambda: self.apply_jobs(),

      ]

      if not os.path.exists(self.config["auth"]["storage_path"]):
        self.auth()
        
      for action in actions:
        human_delay(self.page)
        action()
      
      self.browser.close()

