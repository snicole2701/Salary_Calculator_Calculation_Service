# Salary Calculator - Calculation Service

## Overview
The Calculation Service is a Flask-based microservice responsible for performing detailed salary calculations, including taxes, deductions, UIF contributions, and net salaries. It integrates seamlessly with Microservice 1 (User Input Service) and Microservice 2 (Tax Tables Service), consuming their data to provide accurate and dynamic calculations.
This microservice forms the final processing layer of the Salary Calculator Backend system, leveraging data from upstream services to compute precise salary information. Its efficient design ensures reliability and scalability for various income and tax scenarios.

## Data Preparation
Dynamic Integration:
- Retrieves user-provided inputs (total_income, projected_annual_income, etc.) from Microservice 1.
- Fetches tax and rebate details from Microservice 2 based on user-provided dates and thresholds.

Modular Design:
- Logic is encapsulated into reusable calculation modules for UIF, tax, deductions, and net salary computations.

## Endpoints
Calculate (POST /calculate):
- Triggers the salary calculation workflow.
- Dynamically queries Microservices 1 and 2 for required data.
- Returns detailed salary calculations in JSON format.

Health Check (GET /health):
- Confirms the readiness and operational status of the Calculation Service.

## Key Features
Accurate Calculations:
- Computes UIF contributions, capped at a maximum of 177.12.
- Calculates annual and monthly tax liabilities for income excluding and including bonus and leave pay.
- Computes total deductions and net salary.

Dynamic Data Retrieval:
- Integrates data from Microservice 1 and Microservice 2.
- Ensures all calculations use up-to-date tax and rebate tables.

Logging and Debugging:
- Comprehensive logging for each calculation step.
- Ensures traceability and ease of debugging.

Environment Variables:
- Securely connects with other services using environment variables:- MICROSERVICE_1_URL
- MICROSERVICE_2_URL

## Deployment
Containerization
- The microservice is containerized using Podman.
- Utilizes a lightweight Python:3.10-slim image to ensure efficient resource utilization.
- We deploy this microservice on Render

## Future Integration
The Calculation Service completes the Salary Calculator Backend system by consuming data from Microservice 1 and Microservice 2 to generate accurate salary calculations. It serves as the final processing layer, ensuring smooth integration and workflow across the system


