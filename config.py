PROJECT_NAME = "Whiskey in the Jar"
VERSION = "0.1.0"
ENVIRONMENT = "development"

DATABASE_NAME = "whiskey.db"

MAX_EMAIL_SIZE_MB = 10
STORE_RAW_EMAILS = True
AUTOMATIC_URL_VISITING = False
AUTOMATIC_ATTACHMENT_OPENING = False

# Brand names and their known legitimate email domains.
BRAND_DOMAINS = {
    "microsoft": ["microsoft.com"],
    "amazon": ["amazon.com"],
    "paypal": ["paypal.com"],
    "apple": ["apple.com"],
    "google": ["google.com"],
    "netflix": ["netflix.com"],
}
