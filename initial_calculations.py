import logging

def perform_initial_calculations(data):
    """
    Perform calculations before sending data to Microservice 2.
    Args:
        data (dict): User input data.
    Returns:
        dict: Intermediate calculation results including age group.
    """
    logging.info("[perform_initial_calculations] Start")
    logging.info(f"[perform_initial_calculations] Input data: {data}")

    # Extract salary-related fields
    basic_salary = data.get("basic_salary", 0)
    commission = data.get("commission", 0)
    bonus = data.get("bonus", 0)
    overtime = data.get("overtime", 0)
    leave_pay = data.get("leave_pay", 0)

    logging.debug(f"[perform_initial_calculations] Salaries: basic_salary={basic_salary}, commission={commission}, "
                  f"bonus={bonus}, overtime={overtime}, leave_pay={leave_pay}")

    # Perform financial calculations
    total_income = basic_salary + commission + bonus + overtime + leave_pay
    total_income_excluding_commission = basic_salary + bonus + overtime + leave_pay
    projected_annual_income = total_income * 12
    projected_annual_income_plus_bonus_leave = (total_income + bonus + leave_pay) * 12

    # Determine the age group
    age = data.get("age", 0)
    if 0 <= age <= 64:
        age_group = "Primary"
    elif 65 <= age <= 74:
        age_group = "Secondary (65 and older)"
    elif age >= 75:
        age_group = "Tertiary (75 and older)"
    else:
        raise ValueError("Invalid age value provided.")
    
    logging.info(f"[perform_initial_calculations] Age group determined: {age_group}")

    # Return all intermediate results, including age group
    intermediate_results = {
        "total_income": total_income,
        "total_income_excluding_commission": total_income_excluding_commission,
        "projected_annual_income": projected_annual_income,
        "projected_annual_income_plus_bonus_leave": projected_annual_income_plus_bonus_leave,
        "age_group": age_group
    }

    logging.info(f"[perform_initial_calculations] Intermediate results: {intermediate_results}")
    logging.info("[perform_initial_calculations] End")
    return intermediate_results