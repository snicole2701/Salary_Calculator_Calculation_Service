# config.py
import os

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
TAX_SERVICE_BASE_URL = os.getenv("TAX_SERVICE_BASE_URL", "https://salary-calculator-tax-tables-service.onrender.com")
USER_INPUT_SERVICE_URL = os.getenv("USER_INPUT_SERVICE_URL", "https://salary-calculator-user-input.onrender.com")
FEEDBACK_SERVICE_BASE_URL = "http://example-feedback-service-url.com"