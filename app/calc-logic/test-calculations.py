import pytest
from calculations import (
    calculate_uif,
    calculate_tax_on_income_excluding_bonus_and_leave,
    calculate_tax_on_bonus_and_leave,
    calculate_nett_salary,
    perform_calculations
)

def test_calculate_uif():
    uif = calculate_uif(10000)  # 1% of 10000 is 100
    assert uif == 100

    uif = calculate_uif(20000)  # 1% of 20000 is 200, but capped at 177.12
    assert uif == 177.12

def test_calculate_tax_on_income_excluding_bonus_and_leave():
    projected_annual_income = 500000
    min_income = 400000
    tax_on_previous_brackets = 50000
    tax_percentage = 25
    rebate_value = 15000

    annual_tax, monthly_tax = calculate_tax_on_income_excluding_bonus_and_leave(
        projected_annual_income,
        min_income,
        tax_on_previous_brackets,
        tax_percentage,
        rebate_value
    )

    assert annual_tax == 60000  # Corrected
    assert monthly_tax == 60000 / 12

def test_calculate_tax_on_bonus_and_leave():
    projected_annual_income_plus_bonus_leave = 600000
    min_income_plus_bonus_leave = 400000
    tax_on_previous_brackets_plus_bonus_leave = 50000
    tax_percentage_plus_bonus_leave = 30
    rebate_value = 15000
    annual_tax_excluding_bonus_and_leave = 60000

    tax_on_bonus_and_leave, total_tax = calculate_tax_on_bonus_and_leave(
        projected_annual_income_plus_bonus_leave,
        min_income_plus_bonus_leave,
        tax_on_previous_brackets_plus_bonus_leave,
        tax_percentage_plus_bonus_leave,
        rebate_value,
        annual_tax_excluding_bonus_and_leave
    )

    assert tax_on_bonus_and_leave == 35000  # Corrected expectation
    assert total_tax == 35000 + (60000 / 12)  # Corrected expectation

def test_perform_calculations():
    total_income = 30000
    total_income_excluding_commission = 28000
    projected_annual_income = 500000
    projected_annual_income_plus_bonus_leave = 600000
    tax_details_excluding_bonus_and_leave = {
        "min_income": 400000,
        "tax_on_previous_brackets": 50000,
        "tax_percentage": 25
    }
    tax_details_including_bonus_and_leave = {
        "min_income": 400000,
        "tax_on_previous_brackets": 50000,
        "tax_percentage": 30
    }
    rebate_value = 15000

    results = perform_calculations(
        total_income,
        total_income_excluding_commission,
        projected_annual_income,
        projected_annual_income_plus_bonus_leave,
        tax_details_excluding_bonus_and_leave,
        tax_details_including_bonus_and_leave,
        rebate_value
    )

    assert results["uif"] == 177.12
    assert results["annual_tax_excluding_bonus_and_leave"] == 60000
    assert results["monthly_tax_excluding_bonus_and_leave"] == 60000 / 12
    assert results["tax_on_bonus_and_leave"] == 35000  # Corrected expectation
    assert results["total_tax"] == 35000 + (60000 / 12)
    assert results["total_deductions"] == results["total_tax"] + results["uif"]
    assert results["total_nett_salary"] == total_income - results["total_deductions"]