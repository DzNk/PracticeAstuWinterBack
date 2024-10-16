import os

from dotenv import load_dotenv, find_dotenv
from fastapi.templating import Jinja2Templates

load_dotenv(find_dotenv())

PG_LOGIN = os.getenv("PG_LOGIN")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_PORT = os.getenv("PG_PORT")
PG_HOST = os.getenv("PG_HOST")
PG_DATABASE = os.getenv("PG_DATABASE")

# Api prefix
API_ROOT_PREFIX = os.getenv("API_ROOT_PREFIX")

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY")
SECURITY_ALGORITHM = os.getenv("SECURITY_ALGORITHM")

TEMPLATES = Jinja2Templates(directory="templates")
