"""Sales Agent - Handles loan requirement collection and EMI calculation"""
from typing import Dict, Any
import re

from agents.base_agent import BaseAgent
from models.state import SalesOutput
from utils.emi_calculator import calculate_emi, get_interest_range


class SalesAgent(BaseAgent):
    """
    Sales Agent collects loan requirements and provides EMI estimates.
    Stateless worker agent invoked by Master Agent.
    """
    
    def execute(self, input_data: Dict[str, Any], context: Dict) -> SalesOutput:
        """
        Process loan request and calculate EMI
        
        Args:
            input_data: Dict with 'requested_amount' and 'tenure_months'
            context: Session context
        
        Returns:
            SalesOutput with loan details and EMI calculation
        """
        requested_amount = input_data.get("requested_amount")
        tenure_months = input_data.get("tenure_months")
        
        if not requested_amount or not tenure_months:
            raise ValueError("Missing required fields: requested_amount and tenure_months")
        
        # Get interest range based on amount
        interest_range = get_interest_range(requested_amount)
        
        # Calculate EMI using mid-point of interest range
        mid_rate = self._get_mid_rate(interest_range)
        estimated_emi = calculate_emi(requested_amount, mid_rate, tenure_months)
        
        return SalesOutput(
            requested_amount=requested_amount,
            tenure_months=tenure_months,
            estimated_emi=estimated_emi,
            interest_range=interest_range
        )
    
    def _get_mid_rate(self, interest_range: str) -> float:
        """Extract mid-point rate from interest range string"""
        # Parse "11.5% - 14%" -> 12.75
        match = re.findall(r'(\d+\.?\d*)', interest_range)
        if len(match) >= 2:
            low = float(match[0])
            high = float(match[1])
            return (low + high) / 2
        return 12.0  # Default fallback
