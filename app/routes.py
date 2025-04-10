from flask import Blueprint, jsonify
from app.db import fetch_user_input, fetch_tax_details, fetch_rebate_value
import logging

# Get the logger
logger = logging.getLogger(__name__)

# Define the Blueprint for calculations
calculation_bp = Blueprint('calculation', __name__)

def error_response(message, status_code):
    """
    Helper function to format error responses.
    Args:
        message (str): The error message to return.
        status_code (int): The HTTP status code for the response.
    Returns:
        Response: JSON response with error message and status code.
    """
    logger.error(message)
    return jsonify({"error": message}), status_code

@calculation_bp.route('/calculate', methods=['POST'])
def calculate():
    """Perform tax and rebate calculations based on user input."""
    try:
        logger.info("Starting the calculation process...")

        # Step 1: Fetch user input from Microservice 1
        logger.info("Fetching user input from the User Input Service...")
        user_input = fetch_user_input()
        if not user_input:
            return error_response("Failed to fetch user input.", 500)

        # Extract required data from user input
        total_income = user_input.get("total_income")
        total_income_excluding_commission = user_input.get("total_income_excluding_commission")
        projected_annual_income = user_input.get("projected_annual_income")
        projected_annual_income_plus_bonus_leave = user_input.get("projected_annual_income_plus_bonus_leave")
        month = user_input.get("month")
        year = user_input.get("year")

        if not all([total_income, total_income_excluding_commission, projected_annual_income, projected_annual_income_plus_bonus_leave, month, year]):
            return error_response(
                "Incomplete user input received. Required fields: total_income, total_income_excluding_commission, projected_annual_income, "
                "projected_annual_income_plus_bonus_leave, month, year.",
                400
            )

        # Validate data types
        if not isinstance(total_income, (int, float)) or not isinstance(total_income_excluding_commission, (int, float)) \
                or not isinstance(projected_annual_income, (int, float)) or not isinstance(projected_annual_income_plus_bonus_leave, (int, float)) \
                or not isinstance(month, int) or not isinstance(year, int):
            return error_response(
                "Invalid data types in user input. Ensure total_income, total_income_excluding_commission, projected_annual_income, "
                "and projected_annual_income_plus_bonus_leave are numbers and month/year are integers.",
                400
            )

        # Step 2: Fetch tax details from Microservice 2
        logger.info("Fetching tax details from the Tax Table Service...")
        tax_details = fetch_tax_details(month, year, projected_annual_income, projected_annual_income_plus_bonus_leave)
        if not tax_details:
            return error_response("Failed to fetch tax details.", 500)

        # Extract tax details for calculations
        projected_tax_min_income = tax_details.get("projected_annual_income_min_income")
        projected_tax_on_brackets = tax_details.get("projected_annual_income_tax_on_previous_brackets")
        projected_tax_percentage = tax_details.get("projected_annual_income_tax_percentage")
        income_tax_min_income = tax_details.get("income_tax_min_income")
        income_tax_on_brackets = tax_details.get("income_tax_on_previous_brackets")
        income_tax_percentage = tax_details.get("income_tax_percentage")

        if not all([projected_tax_min_income, projected_tax_on_brackets, projected_tax_percentage,
                    income_tax_min_income, income_tax_on_brackets, income_tax_percentage]):
            return error_response("Missing tax details required for calculations.", 500)

        # Step 3: Fetch rebate value from Microservice 2
        logger.info("Fetching rebate value from the Tax Table Service...")
        rebate_data = fetch_rebate_value()
        rebate_value = rebate_data.get("rebate_value") if rebate_data else None

        if not rebate_value:
            return error_response("Failed to fetch rebate value.", 500)

        # Step 4: Perform calculations
        logger.info("Performing tax calculations...")

        # Tax liability calculation for projected_annual_income
        projected_tax_liability = projected_tax_on_brackets + (projected_annual_income * (projected_tax_percentage / 100)) - rebate_value

        # Tax liability calculation for projected_annual_income_plus_bonus_leave
        income_tax_liability = income_tax_on_brackets + (projected_annual_income_plus_bonus_leave * (income_tax_percentage / 100)) - rebate_value

        logger.info("Calculations completed successfully.")

        # Step 5: Return results
        return jsonify({
            "total_income": total_income,
            "total_income_excluding_commission": total_income_excluding_commission,
            "projected_tax_liability": projected_tax_liability,
            "income_tax_liability": income_tax_liability,
            "rebate_value": rebate_value,
            "tax_details": tax_details,
            "user_input": user_input
        }), 200

    except Exception as e:
        logger.error(f"An unexpected error occurred during calculation: {e}")
        return error_response(f"An unexpected error occurred: {str(e)}", 500)