import os, re
from utils import human_delay
from qna import input_field_factory

class LinkedinAutomation:
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
    self.page.goto("https://www.linkedin.com/login")

    self.page.get_by_label("Email or Phone").fill(self.config["auth"]["email"])
    self.page.get_by_label("Password").fill(self.config["auth"]["password"])
    self.page.get_by_role("button", name="Sign in", exact=True).click()

    # Wait for the homepage to load
    self.page.wait_for_url(re.compile(r".*linkedin\.com/(feed|jobs).*"), timeout=15000)

    # store auth data into a file
    self.context.storage_state(path=self.config["auth"]["storage_path"])

  def search_position_and_location(self):
    self.page.get_by_role('combobox', name=re.compile("Search by title, skill, or")).fill(self.config["search"].get("position", "Backend Developer"))
    self.page.get_by_role('combobox', name=re.compile("City, state, or zip code")).fill(self.config["search"].get("location", "Indonesia"))
    self.page.get_by_role("button", name="Search", exact=True).click()

  def apply_easy_apply_filter(self):
      self.page.get_by_role('radio', name="Easy Apply filter.").click()

  def apply_time_range_filter(self):
      """
      Apply time range filter on when jobs are posted
      """
      label_map = {
         "anytime": "",
         "pastmonth": "r2592000",
         "pastweek": "r604800",
         "past24h": "r86400"
      }[self.config["search"].get("time_range", "anytime")]
      selector_label = f'label[for="timePostedRange-{label_map}"]'
      
      self.page.get_by_role("button", name=re.compile("Date posted filter", re.I)).click()
      self.page.wait_for_selector(selector_label, state="visible", timeout=5000)
      self.page.click(selector_label)
      self.page.get_by_role("button", name=re.compile("Apply current filter to show", re.I)).click()

  def answer_questions(self):
      fields = self.page.locator("form .fb-dash-form-element").all()
      for item in fields:
          field = input_field_factory(item, self.store)

          if field.is_optional():
              continue
          
          if field.is_empty():
            field.answer()

          elif field.has_error():
            field.clear_answer()
            field.retry_answer()

  def click_modal_dismiss(self):
      modal = self.page.locator('div[role="dialog"]').last
      modal.get_by_role("button", name=re.compile("Dismiss")).click()

  def _company_filter_match(self, company_name: str):
    blacklist = self.config["search"].get("company_blacklist", [])
    for company in blacklist:
      if company.casefold() in company_name.casefold():
          return True
    
    return False

  def apply_remote_filter(self):
      param_mapping = {
        "onsite": "On-site",
        "hybrid": "Hybrid",
        "remote": "Remote"
      }

      self.page.get_by_role("button", name=re.compile("Remote filter. Clicking this")).click()
      for param in self.config["search"].get("remote_filter", []):
        val = param_mapping[param]
        self.page.locator('label').filter(has_text=f"{val} Filter by {val}").click()
      
      self.page.get_by_role('button', name=re.compile("Apply current filter to show")).click()
    
  def apply_experience_level_filter(self):
      param_mapping = {
        "intern": "Internship",
        "entry": "Entry level",
        "mid-senior": "Mid-Senior level",
        "director": "Director",
        "executive": "Executive"
      }

      self.page.get_by_role("button", name=re.compile("Experience level filter.")).click()
      for param in self.config["search"].get("experience", []):
        val = param_mapping[param]
        self.page.locator('label').filter(has_text=f"{val} Filter by {val}").click()
      
      self.page.get_by_role('button', name=re.compile("Apply current filter to show")).click()
    
  def apply_jobs(self):
      job_limit = self.config["search"].get("job_limit", 3)
      self.page.wait_for_selector("li[data-occludable-job-id]", timeout=15000)

      # Grab job cards via the attribute-based approach
      job_items = self.page.locator("li[data-occludable-job-id]")
      limit = min(job_limit, job_items.count())

      easy_apply_button = self.page.get_by_role("button", name=re.compile("Easy Apply to"))
      submit_application_button = self.page.get_by_role("button", name=re.compile("Submit application"))
      review_button = self.page.get_by_role("button", name=re.compile("Review your application"))
      next_button = self.page.get_by_role("button", name=re.compile("Continue to next step"))
      follow_company_checkbox = self.page.locator("input#follow-company-checkbox")

      for i in range(limit):
          job = job_items.nth(i)
          job.click()
          
          company_locator = self.page.locator(
             "div.job-details-jobs-unified-top-card__company-name a"
             )
          if company_locator.count():
            company_name = company_locator.inner_text().strip()
            if self._company_filter_match(company_name):
              continue

          if not easy_apply_button.count():
              continue
          
          human_delay(self.page)
          easy_apply_button.click()


          while not submit_application_button.count():
              self.answer_questions()

              human_delay(self.page)
              if next_button.count():
                  next_button.click()
              
              if review_button.count():
                  review_button.click()

          if follow_company_checkbox.count():
              follow_company_checkbox.set_checked(False, force=True)

          human_delay(self.page)
          submit_application_button.click()

          human_delay(self.page)
          self.click_modal_dismiss()

          print(f"Applied job #{i+1}")
          human_delay(self.page)

  def run(self):
    actions = [
      lambda: self.page.goto("https://linkedin.com/jobs/search"),
      lambda: self.search_position_and_location(),
      lambda: self.apply_easy_apply_filter(),
      lambda: self.apply_time_range_filter(),
      lambda: self.apply_remote_filter(),
      lambda: self.apply_experience_level_filter(),
      lambda: self.apply_jobs()
    ]

    if os.path.exists(self.config["auth"]["storage_path"]):
      self.page.goto("https://linkedin.com/jobs/search")

      # verify we didn’t get bounced to /feed
      if "/feed" in self.page.url:
          print("re-authenticating...")
          self.auth()

    else:
      self.auth()

    for action in actions:
      human_delay(self.page)
      action()
    
    self.browser.close()

    

