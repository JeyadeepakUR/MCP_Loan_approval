"""EMI calculation utilities"""


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate EMI using the standard formula:
    EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (percentage, e.g., 12.5)
        tenure_months: Loan tenure in months
    
    Returns:
        Monthly EMI amount
    """
    if tenure_months == 0:
        return 0.0
    
    # Convert annual rate to monthly rate
    monthly_rate = annual_rate / (12 * 100)
    
    if monthly_rate == 0:
        # If rate is 0, EMI is simply principal divided by tenure
        return principal / tenure_months
    
    # EMI formula
    emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / \
          (((1 + monthly_rate) ** tenure_months) - 1)
    
    return round(emi, 2)


def calculate_total_interest(emi: float, tenure_months: int, principal: float) -> float:
    """
    Calculate total interest payable over the loan tenure
    
    Args:
        emi: Monthly EMI
        tenure_months: Loan tenure in months
        principal: Loan amount
    
    Returns:
        Total interest amount
    """
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    
    return round(total_interest, 2)


def get_interest_range(loan_amount: int) -> str:
    """
    Get interest rate range based on loan amount brackets
    
    Args:
        loan_amount: Requested loan amount
    
    Returns:
        Interest range string (e.g., "11.5% - 14%")
    """
    if loan_amount < 300000:  # < 3L
        return "13% - 15%"
    elif loan_amount <= 1000000:  # 3-10L
        return "11.5% - 14%"
    else:  # > 10L
        return "10.5% - 13%"
