"""Sanction Letter Agent - Generates loan sanction letter PDF"""
from typing import Dict, Any

from agents.base_agent import BaseAgent
from models.agent_io import SanctionInput, SanctionOutput
from utils.pdf_generator import generate_sanction_letter


class SanctionAgent(BaseAgent):
    """
    Sanction Letter Agent generates professional PDF sanction letters.
    """
    
    def execute(self, input_data: Dict[str, Any], context: Dict) -> SanctionOutput:
        """
        Generate sanction letter PDF
        
        Args:
            input_data: Dict with all required sanction letter fields
            context: Session context
        
        Returns:
            SanctionOutput with file path and metadata
        """
        # Create SanctionInput from dict
        sanction_input = SanctionInput(**input_data)
        
        # Generate PDF
        file_path, sanction_id = generate_sanction_letter(sanction_input)
        
        return SanctionOutput(
            letter_path=file_path,
            sanction_id=sanction_id,
            validity_days=30,
            metadata={
                "customer_id": sanction_input.customer_id,
                "approved_amount": sanction_input.approved_amount,
                "interest_rate": sanction_input.final_interest_rate,
                "tenure_months": sanction_input.tenure_months
            }
        )
