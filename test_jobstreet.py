import re

from stores import ShelveStore
from utils import load_config
from sites import JobstreetAutomation

from playwright.sync_api import sync_playwright


config = load_config("./conf/jobstreet.yaml")

with sync_playwright() as p:
    with ShelveStore(config["qna"]["storage_path"]) as store:
        app = JobstreetAutomation(config=config, store=store, browser=p.chromium.launch(headless=False))
        app.init()
        app.run()