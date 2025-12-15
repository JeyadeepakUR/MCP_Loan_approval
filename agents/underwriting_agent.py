"""Underwriting Agent - Credit decisioning with deterministic rules"""
from typing import Dict, Any

from agents.base_agent import BaseAgent
from models.state import UnderwritingOutput
from models.enums import UnderwritingDecision
from services.mock_data import MockCreditScoreAPI


class UnderwritingAgent(BaseAgent):
    """
    Underwriting Agent applies deterministic eligibility rules.
    Decision is separated from explanation for Master Agent to handle.
    """
    
    # Interest rate bounds
    MIN_INTEREST_RATE = 9.5
    MAX_INTEREST_RATE = 18.0
    BASE_RATE = 11.0
    
    def __init__(self, audit_logger):
        super().__init__(audit_logger)
        self.credit_api = MockCreditScoreAPI()
    
    def execute(self, input_data: Dict[str, Any], context: Dict) -> UnderwritingOutput:
        """
        Evaluate loan eligibility with deterministic rules
        
        Args:
            input_data: Dict with 'customer_id', 'requested_amount', 'tenure_months', 
                       'monthly_income', 'estimated_emi'
            context: Session context
        
        Returns:
            UnderwritingOutput with decision and rate components
        """
        customer_id = input_data.get("customer_id")
        requested_amount = input_data.get("requested_amount")
        tenure_months = input_data.get("tenure_months")
        monthly_income = input_data.get("monthly_income")
        estimated_emi = input_data.get("estimated_emi")
        
        if not all([customer_id, requested_amount, tenure_months, monthly_income, estimated_emi]):
            raise ValueError("Missing required underwriting parameters")
        
        # Fetch credit score
        credit_score = self.credit_api.get_credit_score(customer_id)
        
        # Apply eligibility rules
        decision, approved_amount, rejection_reason = self._evaluate_eligibility(
            credit_score, monthly_income, requested_amount, estimated_emi
        )
        
        # Calculate interest rate with bounds
        rate_components = self._calculate_rate_components(credit_score, tenure_months)
        final_rate = self._apply_rate_bounds(
            self.BASE_RATE + rate_components["credit_adjustment"] + rate_components["tenure_adjustment"]
        )
        
        # Determine risk grade
        risk_grade = self._calculate_risk_grade(credit_score)
        
        return UnderwritingOutput(
            decision=decision,
            approved_amount=approved_amount,
            credit_score=credit_score,
            rate_components=rate_components,
            final_interest_rate=final_rate,
            risk_grade=risk_grade
        )
    
    def _evaluate_eligibility(
        self, 
        credit_score: int, 
        monthly_income: float, 
        requested_amount: int, 
        estimated_emi: float
    ) -> tuple[str, int, str]:
        """
        Apply deterministic eligibility rules
        
        Returns:
            (decision, approved_amount, rejection_reason)
        """
        # Rule 1: Credit score must be >= 700
        if credit_score < 700:
            return UnderwritingDecision.REJECTED, 0, "Credit score below threshold (700)"
        
        # Rule 2: EMI must not exceed 50% of monthly income
        if estimated_emi > (monthly_income * 0.5):
            return UnderwritingDecision.REJECTED, 0, "EMI exceeds 50% of monthly income"
        
        # Rule 3: Determine max eligible amount based on credit score and income
        if credit_score >= 750 and monthly_income >= 75000:
            max_amount = 2000000
        elif credit_score >= 700 and monthly_income >= 50000:
            max_amount = 1000000
        else:
            max_amount = 500000
        
        # Rule 4: Check if requested amount exceeds max eligible
        if requested_amount > max_amount:
            return UnderwritingDecision.CONDITIONAL, max_amount, f"Approved for maximum eligible amount"
        
        return UnderwritingDecision.APPROVED, requested_amount, ""
    
    def _calculate_rate_components(self, credit_score: int, tenure_months: int) -> Dict[str, float]:
        """
        Calculate interest rate components separately
        
        Returns:
            Dict with base, credit_adjustment, tenure_adjustment
        """
        # Credit score adjustment: -0.5% per 50 points above 700
        credit_adjustment = 0.0
        if credit_score > 700:
            credit_adjustment = -0.5 * ((credit_score - 700) // 50)
        
        # Tenure adjustment: +0.2% per year above 3 years
        tenure_years = tenure_months / 12
        tenure_adjustment = 0.2 * max(0, tenure_years - 3)
        
        return {
            "base": self.BASE_RATE,
            "credit_adjustment": round(credit_adjustment, 2),
            "tenure_adjustment": round(tenure_adjustment, 2)
        }
    
    def _apply_rate_bounds(self, rate: float) -> float:
        """Apply min/max bounds to interest rate"""
        return round(max(self.MIN_INTEREST_RATE, min(self.MAX_INTEREST_RATE, rate)), 2)
    
    def _calculate_risk_grade(self, credit_score: int) -> str:
        """Determine risk grade based on credit score"""
        if credit_score >= 750:
            return "A+"
        elif credit_score >= 725:
            return "A"
        elif credit_score >= 700:
            return "B+"
        elif credit_score >= 675:
            return "B"
        else:
            return "C+"
