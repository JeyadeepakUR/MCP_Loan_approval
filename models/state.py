from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

from models.enums import ConversationStage


class Message(BaseModel):
    """Strongly-typed conversation message"""
    role: Literal["customer", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SalesOutput(BaseModel):
    """Output from Sales Agent"""
    requested_amount: int
    tenure_months: int
    estimated_emi: float
    interest_range: str


class VerificationOutput(BaseModel):
    """Output from Verification Agent"""
    kyc_status: str
    employment_type: str
    monthly_income: float
    risk_flags: List[str] = Field(default_factory=list)


class UnderwritingOutput(BaseModel):
    """Output from Underwriting Agent - decision separated from explanation"""
    decision: Literal["APPROVED", "CONDITIONAL", "REJECTED"]
    approved_amount: int
    credit_score: int
    rate_components: dict  # {"base": 11.0, "credit_adjustment": -1.0, "tenure_adjustment": 0.2}
    final_interest_rate: float
    risk_grade: str


class ConversationState(BaseModel):
    """Central conversation state with strongly-typed messages"""
    session_id: str
    current_stage: ConversationStage
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    sales_data: Optional[SalesOutput] = None
    kyc_data: Optional[VerificationOutput] = None
    underwriting_data: Optional[UnderwritingOutput] = None
    sanction_letter_path: Optional[str] = None
    conversation_history: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
