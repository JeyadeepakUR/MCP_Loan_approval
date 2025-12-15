"""Verification Agent - Handles KYC validation and risk flagging"""
from typing import Dict, Any
import re

from agents.base_agent import BaseAgent
from models.state import VerificationOutput
from models.enums import KYCStatus
from services.mock_data import MockCRMService


class VerificationAgent(BaseAgent):
    """
    Verification Agent validates KYC details using mock CRM.
    Flags basic risks and data mismatches.
    """
    
    def __init__(self, audit_logger):
        super().__init__(audit_logger)
        self.crm_service = MockCRMService()
    
    def execute(self, input_data: Dict[str, Any], context: Dict) -> VerificationOutput:
        """
        Verify customer KYC details
        
        Args:
            input_data: Dict with 'name', 'pan', 'employment_type'
            context: Session context
        
        Returns:
            VerificationOutput with KYC status and risk flags
        """
        name = input_data.get("name", "").strip()
        pan = input_data.get("pan", "").strip().upper()
        employment_type = input_data.get("employment_type", "").strip().upper()
        
        if not name or not pan or not employment_type:
            raise ValueError("Missing required fields: name, pan, employment_type")
        
        # Validate PAN format
        if not self._validate_pan_format(pan):
            return VerificationOutput(
                kyc_status=KYCStatus.FAILED,
                employment_type="UNKNOWN",
                monthly_income=0,
                risk_flags=["INVALID_PAN_FORMAT"]
            )
        
        # Verify with CRM
        is_valid, customer_id, customer_data = self.crm_service.verify_customer(
            name, pan, employment_type
        )
        
        if not is_valid or not customer_data:
            return VerificationOutput(
                kyc_status=KYCStatus.FAILED,
                employment_type=employment_type,
                monthly_income=0,
                risk_flags=["CUSTOMER_NOT_FOUND" if not customer_data else "DATA_MISMATCH"]
            )
        
        # Check for risk flags
        risk_flags = []
        monthly_income = customer_data.get("monthly_income", 0)
        
        if monthly_income < 25000:
            risk_flags.append("LOW_INCOME")
        
        if customer_data.get("employment_type") != employment_type:
            risk_flags.append("EMPLOYMENT_TYPE_MISMATCH")
        
        # Update context with customer_id
        context["customer_id"] = customer_id
        context["customer_name"] = customer_data.get("name")
        
        return VerificationOutput(
            kyc_status=KYCStatus.VERIFIED,
            employment_type=customer_data.get("employment_type"),
            monthly_income=monthly_income,
            risk_flags=risk_flags
        )
    
    def _validate_pan_format(self, pan: str) -> bool:
        """Validate PAN format: 5 letters, 4 digits, 1 letter"""
        pattern = r'^[A-Z]{5}\d{4}[A-Z]$'
        return bool(re.match(pattern, pan))
