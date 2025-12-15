from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class IntentDetectionResult(BaseModel):
    """Result from LLM intent detection with confidence scoring"""
    intent: str  # e.g., "provide_loan_amount", "confirm_kyc"
    confidence: float  # 0.0 to 1.0
    requires_clarification: bool
    
    @property
    def is_confident(self) -> bool:
        """Check if confidence meets threshold (0.7)"""
        return self.confidence >= 0.7


class SalesInput(BaseModel):
    """Input to Sales Agent"""
    user_message: str
    conversation_context: List[dict] = Field(default_factory=list)


class VerificationInput(BaseModel):
    """Input to Verification Agent"""
    customer_id: Optional[str] = None
    name: str
    pan: str
    employment_type: str


class UnderwritingInput(BaseModel):
    """Input to Underwriting Agent"""
    customer_id: str
    requested_amount: int
    tenure_months: int
    monthly_income: float


class SanctionInput(BaseModel):
    """Input to Sanction Letter Agent"""
    session_id: str
    customer_name: str
    customer_id: str
    approved_amount: int
    tenure_months: int
    final_interest_rate: float
    estimated_emi: float
    risk_grade: str


class SanctionOutput(BaseModel):
    """Output from Sanction Letter Agent"""
    letter_path: str
    sanction_id: str
    validity_days: int = 30
    metadata: dict = Field(default_factory=dict)
