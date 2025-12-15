"""Models package for loan origination system"""
from models.enums import ConversationStage, KYCStatus, UnderwritingDecision, EmploymentType
from models.state import Message, ConversationState, SalesOutput, VerificationOutput, UnderwritingOutput
from models.agent_io import (
    IntentDetectionResult,
    SalesInput,
    VerificationInput,
    UnderwritingInput,
    SanctionInput,
    SanctionOutput
)

__all__ = [
    "ConversationStage",
    "KYCStatus",
    "UnderwritingDecision",
    "EmploymentType",
    "Message",
    "ConversationState",
    "SalesOutput",
    "VerificationOutput",
    "UnderwritingOutput",
    "IntentDetectionResult",
    "SalesInput",
    "VerificationInput",
    "UnderwritingInput",
    "SanctionInput",
    "SanctionOutput",
]
