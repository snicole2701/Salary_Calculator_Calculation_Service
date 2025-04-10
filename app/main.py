import logging
import os
import requests
from . import create_app
from .db import check_tax_service_health, fetch_user_input, fetch_tax_details, fetch_rebate_value

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting Calculation Service...")

# Microservices URLs
MICROSERVICE_1_URL = "https://salary-calculator-user-input.onrender.com"
MICROSERVICE_2_URL = "https://salary-calculator-tax-tables-service.onrender.com"

# Create the Flask app
app = create_app()

# Pre-startup Health Checks
try:
    # Check health of Tax Table Service
    if not check_tax_service_health():
        logger.error("Tax Table Service is unavailable. Calculation Service cannot start.")
        raise SystemExit("Dependency check failed: Tax Table Service is unavailable.")

    # Test User Input Service (fetch user input as a health check)
    user_input = fetch_user_input()
    if user_input is None:
        logger.error("User Input Service is unavailable. Calculation Service cannot start.")
        raise SystemExit("Dependency check failed: User Input Service is unavailable.")

    logger.info("All dependent services are healthy. Proceeding with service startup.")
except Exception as e:
    logger.error(f"Error during service dependency checks: {e}")
    raise SystemExit("Dependency check failed: Service startup aborted.")

# Function to fetch data and calculate
def fetch_and_calculate():
    """
    Fetch data from Microservices 1 and 2 and perform calculations.
    """
    logger.info("Starting data retrieval and calculation process...")

    # Step 1: Fetch data from Microservice 1
    user_data = fetch_user_input()
    if not user_data:
        logger.error("Failed to fetch data from Microservice 1.")
        return

    # Extract required fields
    total_income = user_data.get("total_income")
    total_income_excluding_commission = user_data.get("total_income_excluding_commission")
    projected_annual_income = user_data.get("projected_annual_income")
    projected_annual_income_plus_bonus_leave = user_data.get("projected_annual_income_plus_bonus_leave")

    if not all([total_income, total_income_excluding_commission, projected_annual_income, projected_annual_income_plus_bonus_leave]):
        logger.error("Incomplete data from Microservice 1.")
        return

    # Step 2: Fetch tax details from Microservice 2
    month = user_data.get("month")
    year = user_data.get("year")
    tax_details = fetch_tax_details(month, year, projected_annual_income, projected_annual_income_plus_bonus_leave)
    if not tax_details:
        logger.error("Failed to fetch tax details from Microservice 2.")
        return

    # Extract tax details
    projected_tax_min_income = tax_details.get("projected_annual_income_min_income")
    projected_tax_on_brackets = tax_details.get("projected_annual_income_tax_on_previous_brackets")
    projected_tax_percentage = tax_details.get("projected_annual_income_tax_percentage")
    income_tax_min_income = tax_details.get("income_tax_min_income")
    income_tax_on_brackets = tax_details.get("income_tax_on_previous_brackets")
    income_tax_percentage = tax_details.get("income_tax_percentage")

    if not all([projected_tax_min_income, projected_tax_on_brackets, projected_tax_percentage,
                income_tax_min_income, income_tax_on_brackets, income_tax_percentage]):
        logger.error("Incomplete tax details fetched from Microservice 2.")
        return

    # Step 3: Fetch rebate value from Microservice 2
    rebate_data = fetch_rebate_value()
    rebate_value = rebate_data.get("rebate_value") if rebate_data else None

    if not rebate_value:
        logger.error("Failed to fetch rebate value from Microservice 2.")
        return

    # Log retrieved data
    logger.info(f"Data retrieved: Total Income: {total_income}, Total Income Excl Commission: {total_income_excluding_commission}, "
                f"Projected Annual Income: {projected_annual_income}, Projected Annual Income Plus Bonus Leave: {projected_annual_income_plus_bonus_leave}, "
                f"Rebate Value: {rebate_value}, Projected Tax Min Income: {projected_tax_min_income}, "
                f"Projected Tax On Brackets: {projected_tax_on_brackets}, Projected Tax Percentage: {projected_tax_percentage}, "
                f"Income Tax Min Income: {income_tax_min_income}, Income Tax On Brackets: {income_tax_on_brackets}, Income Tax Percentage: {income_tax_percentage}")

    # Step 4: Perform calculations
    logger.info("Performing calculations...")

    # Tax liability calculation for projected_annual_income
    projected_tax_liability = projected_tax_on_brackets + (projected_annual_income * (projected_tax_percentage / 100)) - rebate_value

    # Tax liability calculation for projected_annual_income_plus_bonus_leave
    income_tax_liability = income_tax_on_brackets + (projected_annual_income_plus_bonus_leave * (income_tax_percentage / 100)) - rebate_value

    # Log calculated results
    logger.info(f"Calculated Projected Tax Liability: {projected_tax_liability}")
    logger.info(f"Calculated Income Tax Liability: {income_tax_liability}")

    # Return calculated results
    return {
        "total_income": total_income,
        "total_income_excluding_commission": total_income_excluding_commission,
        "projected_tax_liability": projected_tax_liability,
        "income_tax_liability": income_tax_liability
    }

if __name__ == "__main__":
    try:
        # Dynamically set debug mode based on environment variable
        debug_mode = os.getenv("DEBUG", "False").lower() == "true"
        port = int(os.getenv("PORT", 5002))  # Set the port from an environment variable or default to 5002
        app.run(host="0.0.0.0", port=port, debug=debug_mode)

        # Perform data fetching and calculations
        calculated_results = fetch_and_calculate()
        if calculated_results:
            logger.info(f"Final Calculated Results: {calculated_results}")
    except Exception as e:
        logger.error(f"Error starting the Calculation Service: {e}")