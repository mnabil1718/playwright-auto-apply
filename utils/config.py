import dotenv, os

def load_config() -> dict:
  dotenv.load_dotenv()

  config = {
    "AUTH": {
      "STORAGE_PATH": os.environ["AUTH_STORAGE_PATH"],
      "EMAIL": os.environ["EMAIL"],
      "PASSWORD": os.environ["PASSWORD"],
    },
    "QNA": {
      "STORAGE_PATH": os.environ["QNA_STORE_PATH"]
    },
    "COMPANY_BLACKLIST": ["Diksha", "Super indo"]
  }

  return config