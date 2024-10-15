import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DOMAIN = os.getenv("DOMAIN")

# PostgreSQL database settings
PG_LOGIN = os.getenv("PG_LOGIN")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_PORT = os.getenv("PG_PORT")
PG_HOST = os.getenv("PG_HOST")
PG_DATABASE = os.getenv("PG_DATABASE")

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# S3Client
S3_API_URL = os.getenv("S3_API_URL")
S3_API_KEY = os.getenv("S3_API_KEY")

# Api prefix
API_ROOT_PREFIX = os.getenv("API_ROOT_PREFIX")

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY")
SECURITY_ALGORITHM = os.getenv("SECURITY_ALGORITHM")
