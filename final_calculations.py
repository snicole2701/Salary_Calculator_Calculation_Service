import logging

def calculate_uif(total_income_excluding_commission):
    """Calculate UIF contribution."""
    logging.info("[calculate_uif] Start")
    logging.debug(f"[calculate_uif] Input: total_income_excluding_commission={total_income_excluding_commission}")

    uif = total_income_excluding_commission * 0.01  # 1% calculation
    capped_uif = min(uif, 177.12)  # Cap UIF at a maximum of 177.12

    logging.info(f"[calculate_uif] UIF calculated: {capped_uif}")
    logging.info("[calculate_uif] End")
    return capped_uif

def calculate_nett_salary(total_income, total_deductions):
    """Calculate net salary after deductions."""
    logging.info("[calculate_nett_salary] Start")
    logging.debug(f"[calculate_nett_salary] Inputs: total_income={total_income}, total_deductions={total_deductions}")

    nett_salary = total_income - total_deductions

    logging.info(f"[calculate_nett_salary] Net salary calculated: {nett_salary}")
    logging.info("[calculate_nett_salary] End")
    return nett_salary

def perform_final_calculations(intermediate_data, tax_and_rebate_data):
    """
    Perform final calculations using data from Microservice 2.
    Args:
        intermediate_data (dict): Intermediate calculation results.
        tax_and_rebate_data (dict): Data from Microservice 2.
    Returns:
        dict: Final calculation results.
    """
    logging.info("[perform_final_calculations] Start")
    logging.info(f"[perform_final_calculations] Intermediate data: {intermediate_data}")
    logging.info(f"[perform_final_calculations] Tax and rebate data: {tax_and_rebate_data}")

    try:
        total_income = intermediate_data["total_income"]
        total_income_excluding_commission = intermediate_data["total_income_excluding_commission"]
        projected_annual_income = intermediate_data["projected_annual_income"]
        projected_annual_income_plus_bonus_leave = intermediate_data["projected_annual_income_plus_bonus_leave"]

        tax_details_excluding_bonus_and_leave = tax_and_rebate_data["tax_details_excluding_bonus_and_leave"]
        tax_details_including_bonus_and_leave = tax_and_rebate_data["tax_details_including_bonus_and_leave"]
        rebate_value = tax_and_rebate_data["rebate_value"]

        # Calculate UIF
        uif = calculate_uif(total_income_excluding_commission)

        # Calculate annual and monthly tax on income excluding bonus and leave
        annual_tax_excluding_bonus_and_leave = (
            tax_details_excluding_bonus_and_leave["tax_on_previous_brackets"] +
            ((projected_annual_income - tax_details_excluding_bonus_and_leave["min_income"]) *
             (tax_details_excluding_bonus_and_leave["tax_percentage"] / 100)) -
            rebate_value
        )
        monthly_tax_excluding_bonus_and_leave = annual_tax_excluding_bonus_and_leave / 12

        logging.debug(f"[perform_final_calculations] Tax excluding bonus and leave: "
                      f"annual={annual_tax_excluding_bonus_and_leave}, monthly={monthly_tax_excluding_bonus_and_leave}")

        # Calculate tax on bonus and leave pay
        annual_tax_including_bonus_and_leave = (
            tax_details_including_bonus_and_leave["tax_on_previous_brackets"] +
            ((projected_annual_income_plus_bonus_leave - tax_details_including_bonus_and_leave["min_income"]) *
             (tax_details_including_bonus_and_leave["tax_percentage"] / 100)) -
            rebate_value
        )
        tax_on_bonus_and_leave = annual_tax_including_bonus_and_leave - annual_tax_excluding_bonus_and_leave
        total_tax = monthly_tax_excluding_bonus_and_leave + tax_on_bonus_and_leave

        logging.debug(f"[perform_final_calculations] Tax on bonus and leave: {tax_on_bonus_and_leave}")
        logging.debug(f"[perform_final_calculations] Total tax: {total_tax}")

        # Calculate total deductions and net salary
        total_deductions = total_tax + uif
        total_nett_salary = calculate_nett_salary(total_income, total_deductions)

        final_results = {
            "uif": uif,
            "annual_tax_excluding_bonus_and_leave": annual_tax_excluding_bonus_and_leave,
            "monthly_tax_excluding_bonus_and_leave": monthly_tax_excluding_bonus_and_leave,
            "tax_on_bonus_and_leave": tax_on_bonus_and_leave,
            "total_tax": total_tax,
            "total_deductions": total_deductions,
            "total_nett_salary": total_nett_salary
        }

        logging.info(f"[perform_final_calculations] Final calculation results: {final_results}")

    except Exception as e:
        logging.error(f"[perform_final_calculations] Error: {str(e)}")
        raise

    logging.info("[perform_final_calculations] End")
    return final_results