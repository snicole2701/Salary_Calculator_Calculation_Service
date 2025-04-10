import requests
import logging
from .config import TAX_SERVICE_BASE_URL, USER_INPUT_SERVICE_URL, FEEDBACK_SERVICE_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to check the health of the Tax Table Service
def check_tax_service_health():
    """
    Verify the health status of the Tax Table Service.
    Returns:
        bool: True if the service is healthy, False otherwise.
    """
    url = f"{TAX_SERVICE_BASE_URL}/health"
    logger.info("Checking health of Tax Table Service...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.info("Tax Table Service is healthy!")
            return True
        else:
            logger.warning("Tax Table Service is not healthy!")
            return False
    except requests.RequestException as e:
        logger.error(f"Request to Tax Table Service failed: {e}")
        return False

# Function to fetch user input from the User Input Service
def fetch_user_input():
    """
    Fetch user input from the User Input Service.

    Returns:
        dict: A dictionary containing the following validated user input values:
            - total_income (float): Total income calculated.
            - total_income_excluding_commission (float): Income excluding commission.
            - projected_annual_income (float): Annual income projected (excluding bonus and leave pay).
            - projected_annual_income_plus_bonus_leave (float): Annual income plus bonus and leave pay.
        Returns None if an error occurs or data is incomplete.
    """
    url = f"{USER_INPUT_SERVICE_URL}/validate"
    logger.info("Fetching user input from User Input Service...")
    try:
        response = requests.post(url, json={})
        if response.status_code == 200:
            logger.info("User input successfully fetched.")
            data = response.json().get("data", {})
            # Ensure all required fields are present
            required_fields = [
                "total_income",
                "total_income_excluding_commission",
                "projected_annual_income",
                "projected_annual_income_plus_bonus_leave"
            ]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                logger.error(f"Incomplete data from User Input Service. Missing fields: {missing_fields}")
                return None
            return data
        else:
            logger.error(f"Error fetching user input: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Request to User Input Service failed: {e}")
        return None

# Function to fetch tax details from the Tax Table Service
def fetch_tax_details(month, year, projected_annual_income, projected_annual_income_plus_bonus_leave):
    """
    Fetch applicable tax details for both incomes from the Tax Table Service.
    Args:
        month (int): Month of the year.
        year (int): Year.
        projected_annual_income (float): Projected annual income.
        projected_annual_income_plus_bonus_leave (float): Projected annual income plus bonus and leave pay.
    Returns:
        dict: Tax details for both incomes, including min_income, tax_on_previous_brackets, and tax_percentage.
    """
    url = f"{TAX_SERVICE_BASE_URL}/get-tax-details"
    payload = {
        "month": month,
        "year": year,
        "projected_annual_income": projected_annual_income,
        "projected_annual_income_plus_bonus_leave": projected_annual_income_plus_bonus_leave
    }
    logger.info(f"Fetching tax details for Month: {month}, Year: {year}, Projected Incomes: {projected_annual_income}, {projected_annual_income_plus_bonus_leave}...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info("Tax details successfully fetched.")
            return response.json()  # Expected format: {"projected_annual_income_min_income": ..., "projected_annual_income_tax_on_previous_brackets": ..., "projected_annual_income_tax_percentage": ..., "income_tax_min_income": ..., "income_tax_on_previous_brackets": ..., "income_tax_percentage": ...}
        elif response.status_code == 404:
            logger.warning(f"Tax details not found: {response.json().get('error', 'Unknown error')}")
            return None
        else:
            logger.error(f"Error fetching tax details: {response.json().get('error', 'Unexpected error')}")
            return None
    except requests.RequestException as e:
        logger.error(f"Request to Tax Table Service failed: {e}")
        return None

# Function to fetch rebate value from the Tax Table Service
def fetch_rebate_value():
    """
    Fetch the rebate value retrieved by Microservice 2.
    Returns:
        dict: Contains rebate_value.
    """
    url = f"{TAX_SERVICE_BASE_URL}/get-tax-details"
    logger.info("Fetching rebate value from Tax Table Service...")
    try:
        response = requests.post(url, json={})  # Ensure payload matches Microservice 2's requirements
        if response.status_code == 200:
            logger.info("Rebate value successfully fetched.")
            return {"rebate_value": response.json().get("rebate_value")}
        elif response.status_code == 404:
            logger.warning(f"Rebate value not found: {response.json().get('error', 'Unknown error')}")
            return None
        else:
            logger.error(f"Error fetching rebate value: {response.json().get('error', 'Unexpected error')}")
            return None
    except requests.RequestException as e:
        logger.error(f"Request to Tax Table Service failed: {e}")
        return None

# Placeholder Function for Sending Feedback to Microservice 4
def send_feedback(feedback_data):
    """
    Send feedback data to the Feedback Service (Microservice 4).
    Args:
        feedback_data (dict): Data to send to the service.
    Returns:
        dict: Response from the Feedback Service.
    """
    url = f"{FEEDBACK_SERVICE_BASE_URL}/send-feedback"
    logger.info("Sending feedback to Feedback Service...")
    try:
        response = requests.post(url, json=feedback_data)
        if response.status_code == 200:
            logger.info("Feedback successfully sent.")
            return response.json()
        else:
            logger.error(f"Error sending feedback: {response.status_code}")
            return {"error": response.json().get("error", "Unknown error")}
    except requests.RequestException as e:
        logger.error(f"Failed to connect to Feedback Service: {e}")
        return {"error": "Connection to Feedback Service failed"}