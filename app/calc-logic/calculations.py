def calculate_uif(total_income_excluding_commission):
    """
    Calculate UIF contribution based on total_income_excluding_commission.
    Args:
        total_income_excluding_commission (float): Income excluding commission.
    Returns:
        float: UIF contribution, capped at 177.12.
    """
    uif = total_income_excluding_commission * 0.01  # 1% calculation
    return min(uif, 177.12)  # Cap UIF at a maximum of 177.12


def calculate_tax_on_income_excluding_bonus_and_leave(projected_annual_income, min_income, tax_on_previous_brackets, tax_percentage, rebate_value):
    """
    Calculate annual and monthly tax on income excluding bonus and leave pay.
    Args:
        projected_annual_income (float): Projected annual income.
        min_income (float): Minimum income bracket from tax table.
        tax_on_previous_brackets (float): Tax on previous brackets from tax table.
        tax_percentage (float): Tax percentage from tax table.
        rebate_value (float): Rebate value.
    Returns:
        tuple: Annual and monthly tax on income excluding bonus and leave pay.
    """
    annual_tax = (
        tax_on_previous_brackets +
        ((projected_annual_income - min_income) * (tax_percentage / 100)) -
        rebate_value
    )
    monthly_tax = annual_tax / 12  # Convert annual tax to monthly tax
    return annual_tax, monthly_tax


def calculate_tax_on_bonus_and_leave(
    projected_annual_income_plus_bonus_leave,
    min_income_plus_bonus_leave,
    tax_on_previous_brackets_plus_bonus_leave,
    tax_percentage_plus_bonus_leave,
    rebate_value,
    annual_tax_excluding_bonus_and_leave
):
    """
    Calculate tax on bonus and leave pay.
    Args:
        projected_annual_income_plus_bonus_leave (float): Projected annual income including bonus and leave pay.
        min_income_plus_bonus_leave (float): Minimum income bracket from tax table for bonus and leave.
        tax_on_previous_brackets_plus_bonus_leave (float): Tax on previous brackets for bonus and leave.
        tax_percentage_plus_bonus_leave (float): Tax percentage for bonus and leave.
        rebate_value (float): Rebate value.
        annual_tax_excluding_bonus_and_leave (float): Annual tax on income excluding bonus and leave pay.
    Returns:
        tuple: Tax on bonus and leave pay, total tax, and total deductions.
    """
    annual_tax_including_bonus_and_leave = (
        tax_on_previous_brackets_plus_bonus_leave +
        ((projected_annual_income_plus_bonus_leave - min_income_plus_bonus_leave) * (tax_percentage_plus_bonus_leave / 100)) -
        rebate_value
    )

    tax_on_bonus_and_leave = annual_tax_including_bonus_and_leave - annual_tax_excluding_bonus_and_leave
    total_tax = tax_on_bonus_and_leave + (annual_tax_excluding_bonus_and_leave / 12)  # Total monthly tax

    return tax_on_bonus_and_leave, total_tax


def calculate_nett_salary(total_income, total_deductions):
    """
    Calculate net salary after deductions.
    Args:
        total_income (float): Total monthly income.
        total_deductions (float): Total monthly deductions.
    Returns:
        float: Net monthly salary.
    """
    return total_income - total_deductions


# Wrapper function to perform all calculations
def perform_calculations(
    total_income,
    total_income_excluding_commission,
    projected_annual_income,
    projected_annual_income_plus_bonus_leave,
    tax_details_excluding_bonus_and_leave,
    tax_details_including_bonus_and_leave,
    rebate_value
):
    """
    Perform all calculations including UIF, tax, and net salary.
    Args:
        total_income (float): Total monthly income.
        total_income_excluding_commission (float): Income excluding commission.
        projected_annual_income (float): Projected annual income.
        projected_annual_income_plus_bonus_leave (float): Projected annual income including bonus and leave.
        tax_details_excluding_bonus_and_leave (dict): Tax details for income excluding bonus and leave.
        tax_details_including_bonus_and_leave (dict): Tax details for income including bonus and leave.
        rebate_value (float): Rebate value.
    Returns:
        dict: All calculated values.
    """
    # UIF calculation
    uif = calculate_uif(total_income_excluding_commission)

    # Tax calculation excluding bonus and leave
    annual_tax_excluding_bonus_and_leave, monthly_tax_excluding_bonus_and_leave = calculate_tax_on_income_excluding_bonus_and_leave(
        projected_annual_income,
        tax_details_excluding_bonus_and_leave["min_income"],
        tax_details_excluding_bonus_and_leave["tax_on_previous_brackets"],
        tax_details_excluding_bonus_and_leave["tax_percentage"],
        rebate_value
    )

    # Tax calculation on bonus and leave
    tax_on_bonus_and_leave, total_tax = calculate_tax_on_bonus_and_leave(
        projected_annual_income_plus_bonus_leave,
        tax_details_including_bonus_and_leave["min_income"],
        tax_details_including_bonus_and_leave["tax_on_previous_brackets"],
        tax_details_including_bonus_and_leave["tax_percentage"],
        rebate_value,
        annual_tax_excluding_bonus_and_leave
    )

    # Total deductions
    total_deductions = total_tax + uif

    # Net salary calculation
    total_nett_salary = calculate_nett_salary(total_income, total_deductions)

    return {
        "uif": uif,
        "annual_tax_excluding_bonus_and_leave": annual_tax_excluding_bonus_and_leave,
        "monthly_tax_excluding_bonus_and_leave": monthly_tax_excluding_bonus_and_leave,
        "tax_on_bonus_and_leave": tax_on_bonus_and_leave,
        "total_tax": total_tax,
        "total_deductions": total_deductions,
        "total_nett_salary": total_nett_salary
    }