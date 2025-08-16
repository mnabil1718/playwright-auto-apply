import random

def human_delay(page, min=1000, max=3800):
    delay_duration = random.randint(min, max+1)
    page.wait_for_timeout(delay_duration)
