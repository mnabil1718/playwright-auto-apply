import os
from utils import human_delay

def auth(auth_storage_path, email, password: str, browser):
    if os.path.exists(auth_storage_path):
        context = browser.new_context(storage_state=auth_storage_path)
        page = context.new_page()

    else:
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.linkedin.com/login")

        page.get_by_label("Email or Phone").fill(email)

        human_delay()
        page.get_by_label("Password").fill(password)

        human_delay()
        page.get_by_role("button", name="Sign in", exact=True).click()

        # Wait for the homepage to load
        page.wait_for_load_state("networkidle")

        # store auth data into a file
        context.storage_state(path=auth_storage_path)

    return page, context
