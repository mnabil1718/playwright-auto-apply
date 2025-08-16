import re

from stores import ShelveStore
from utils import load_config
from sites import LinkedinAutomation

from playwright.sync_api import sync_playwright


config = load_config()

with sync_playwright() as p:
    with ShelveStore(config["QNA"]["STORAGE_PATH"]) as store:
        app = LinkedinAutomation(config=config, store=store, browser=p.chromium.launch(headless=False))
        app.run()