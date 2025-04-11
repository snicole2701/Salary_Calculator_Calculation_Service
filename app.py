from flask import Flask, jsonify
import os
import logging
import requests
from initial_calculations import perform_initial_calculations
from final_calculations import perform_final_calculations

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Service URLs
USER_INPUT_SERVICE_BASE_URL = os.getenv("USER_INPUT_SERVICE_BASE_URL", "https://salary-calculator-user-input.onrender.com")
TAX_TABLE_SERVICE_BASE_URL = os.getenv("TAX_TABLE_SERVICE_BASE_URL", "https://salary-calculator-tax-tables-service.onrender.com")

# Validate environment variables
if not USER_INPUT_SERVICE_BASE_URL or not TAX_TABLE_SERVICE_BASE_URL:
    raise ValueError("Environment variables USER_INPUT_SERVICE_BASE_URL and TAX_TABLE_SERVICE_BASE_URL must be set.")

logging.info(f"USER_INPUT_SERVICE_BASE_URL: {USER_INPUT_SERVICE_BASE_URL}")
logging.info(f"TAX_TABLE_SERVICE_BASE_URL: {TAX_TABLE_SERVICE_BASE_URL}")

# Fetch user input from Microservice 1
def fetch_user_input():
    """
    Fetch user input data from Microservice 1.
    Returns:
        dict: User input data or error.
    """
    url = f"{USER_INPUT_SERVICE_BASE_URL}/get-user-input"
    try:
        response = requests.get(url)

        # Check if the response is valid
        if response.status_code == 200 and response.content:  # Ensure content is not empty
            user_input = response.json()

            # Validate required fields
            if not all(key in user_input for key in ["month", "year", "age"]):
                logging.error("User input is missing required fields: month, year, or age.")
                return {"error": "User input is incomplete."}

            logging.info(f"User input fetched successfully: {user_input}")
            return user_input
        elif response.status_code == 400:  # Handle invalid request
            logging.warning("No user input available. Returning error.")
            return {"error": "User input is unavailable."}
        else:
            logging.error(f"Error fetching user input: {response.status_code} - {response.text}")
            return {"error": f"Failed with status code {response.status_code}"}
    except ValueError as e:  # JSON decoding error
        logging.error(f"Failed to decode JSON response: {e}")
        return {"error": "Invalid JSON response from User Input Service"}
    except requests.RequestException as e:
        logging.error(f"Failed to connect to User Input Service: {e}")
        return {"error": "Connection to User Input Service failed"}

# Send data to Microservice 2
def send_to_tax_table_service(data):
    """
    Send income and user data to Microservice 2 for tax and rebate queries.
    Args:
        data (dict): Combined data from user input and intermediate calculations.
    Returns:
        dict: Tax and rebate details from Microservice 2.
    """
    url = f"{TAX_TABLE_SERVICE_BASE_URL}/get-tax-details"
    try:
        logging.info(f"Sending payload to Tax Table Service: {data}")
        response = requests.post(url, json=data)
        if response.status_code == 200:
            tax_and_rebate_data = response.json()
            logging.info(f"Tax and rebate data fetched successfully: {tax_and_rebate_data}")
            return tax_and_rebate_data
        else:
            logging.error(f"Error from Tax Table Service: {response.status_code} - {response.json().get('error', 'Unknown error')}")
            return {"error": response.json().get("error", "Unknown error")}
    except requests.RequestException as e:
        logging.error(f"Failed to connect to Tax Table Service: {e}")
        return {"error": "Connection to Tax Table Service failed"}

@app.route("/", methods=["GET"])
def home():
    """Default route."""
    return jsonify({"message": "Microservice 3 is running successfully!"}), 200

@app.route("/perform-calculations", methods=["POST"])
def perform_calculations_route():
    """Endpoint to perform calculations."""
    logging.info("Accessing /perform-calculations route")

    # Fetch user input
    user_input = fetch_user_input()
    if "error" in user_input:
        return jsonify({"error": user_input["error"]}), 500

    # Perform initial calculations
    intermediate_data = perform_initial_calculations(user_input)

    # Combine user input fields with intermediate calculations
    combined_data = {
        **intermediate_data,  # Includes age_group
        "month": user_input["month"],
        "year": user_input["year"],
        "age": user_input["age"]
    }

    # Send combined data to Microservice 2
    tax_and_rebate_data = send_to_tax_table_service(combined_data)
    if "error" in tax_and_rebate_data:
        return jsonify({"error": tax_and_rebate_data["error"]}), 500

    # Perform final calculations
    final_results = perform_final_calculations(
        intermediate_data,
        tax_and_rebate_data
    )

    return jsonify(final_results), 200

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "OK"}), 200

if __name__ == "__main__":
    logging.info("Starting Flask app for Microservice 3")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5002)))