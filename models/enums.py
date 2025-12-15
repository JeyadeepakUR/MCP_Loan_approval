from enum import Enum


class ConversationStage(str, Enum):
    """Stages in the loan origination conversation flow"""
    SALES = "SALES"
    KYC = "KYC"
    UNDERWRITING = "UNDERWRITING"
    SANCTION = "SANCTION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class KYCStatus(str, Enum):
    """KYC verification status"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class UnderwritingDecision(str, Enum):
    """Underwriting decision outcomes"""
    APPROVED = "APPROVED"
    CONDITIONAL = "CONDITIONAL"
    REJECTED = "REJECTED"


class EmploymentType(str, Enum):
    """Customer employment types"""
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    BUSINESS = "BUSINESS"
