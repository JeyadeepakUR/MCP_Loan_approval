"""Master Agent - Orchestrator for the loan origination conversation flow"""
from typing import Optional, Dict, Any
import uuid

from agents.base_agent import BaseAgent
from agents.sales_agent import SalesAgent
from agents.verification_agent import VerificationAgent
from agents.underwriting_agent import UnderwritingAgent
from agents.sanction_agent import SanctionAgent

from models.enums import ConversationStage, UnderwritingDecision, KYCStatus
from models.state import ConversationState, Message
from services.state_manager import StateManager
from services.audit_logger import AuditLogger
from services.llm_interface import LLMService


class MasterAgent:
    """
    Master Agent (Orchestrator) - Controls all conversation flow and state transitions.
    Only component allowed to communicate directly with the customer.
    """
    
    MAX_RETRIES = 3
    
    def __init__(self):
        """Initialize Master Agent with all services and worker agents"""
        self.state_manager = StateManager()
        self.audit_logger = AuditLogger()
        self.llm_service = LLMService()
        
        # Initialize worker agents
        self.sales_agent = SalesAgent(self.audit_logger)
        self.verification_agent = VerificationAgent(self.audit_logger)
        self.underwriting_agent = UnderwritingAgent(self.audit_logger)
        self.sanction_agent = SanctionAgent(self.audit_logger)
        
        self.current_session_id: Optional[str] = None
        self.retry_count: Dict[str, int] = {}
    
    def start_conversation(self) -> str:
        """
        Start a new conversation session
        
        Returns:
            Welcome message for customer
        """
        # Create new session
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        self.current_session_id = session_id
        
        # Initialize state
        self.state_manager.create_session(session_id)
        
        # Log state transition
        self.audit_logger.log_state_transition(
            session_id=session_id,
            from_stage="NONE",
            to_stage=ConversationStage.SALES,
            reason="New conversation started"
        )
        
        # Add system message
        welcome_msg = (
            "Welcome to BFSI Bank! I'm here to help you with your personal loan application. "
            "To get started, please tell me:\n"
            "1. How much loan amount do you need?\n"
            "2. What is your preferred loan tenure (in years)?"
        )
        
        self.state_manager.add_message(session_id, "system", welcome_msg)
        
        return welcome_msg
    
    def process_message(self, user_message: str) -> str:
        """
        Process user message and return system response
        
        Args:
            user_message: Customer's input message
        
        Returns:
            System response to customer
        """
        if not self.current_session_id:
            return "Error: No active session. Please start a new conversation."
        
        # Load current state
        state = self.state_manager.load_state(self.current_session_id)
        if not state:
            return "Error: Session not found."
        
        # Add user message to history
        self.state_manager.add_message(self.current_session_id, "customer", user_message)
        
        # Detect intent
        intent_result = self.llm_service.detect_intent(
            user_message=user_message,
            current_stage=state.current_stage,
            conversation_history=state.conversation_history
        )
        
        # Check if clarification needed
        if intent_result.requires_clarification:
            response = self._handle_unclear_intent(state, user_message)
        else:
            # Process based on current stage
            response = self._process_by_stage(state, user_message, intent_result.intent)
        
        # Add system response to history
        self.state_manager.add_message(self.current_session_id, "system", response)
        
        return response
    
    def _process_by_stage(self, state: ConversationState, user_message: str, intent: str) -> str:
        """Route processing based on current conversation stage"""
        
        if state.current_stage == ConversationStage.SALES:
            return self._handle_sales_stage(state, user_message, intent)
        
        elif state.current_stage == ConversationStage.KYC:
            return self._handle_kyc_stage(state, user_message, intent)
        
        elif state.current_stage == ConversationStage.UNDERWRITING:
            return self._handle_underwriting_stage(state)
        
        elif state.current_stage == ConversationStage.SANCTION:
            return self._handle_sanction_stage(state)
        
        elif state.current_stage == ConversationStage.COMPLETED:
            return "Your loan application has been completed. Thank you for choosing BFSI Bank!"
        
        elif state.current_stage == ConversationStage.FAILED:
            return "Your loan application was not approved. Please contact our support team for more information."
        
        return "I'm not sure how to help with that. Could you please clarify?"
    
    def _handle_sales_stage(self, state: ConversationState, user_message: str, intent: str) -> str:
        """Handle SALES stage - collect loan requirements"""
        
        # Extract entities from message
        entities = self.llm_service.extract_entities(user_message, intent)
        
        # Check if we have both amount and tenure
        if "amount" in entities and "tenure_months" in entities:
            # Call Sales Agent
            try:
                sales_output = self.sales_agent.run(
                    input_data={
                        "requested_amount": entities["amount"],
                        "tenure_months": entities["tenure_months"]
                    },
                    context={"session_id": state.session_id}
                )
                
                # Update state
                state.sales_data = sales_output
                self.state_manager.save_state(state)
                
                # Transition to KYC
                self._transition_stage(state, ConversationStage.KYC, "Sales data collected")
                
                # Return customer-friendly message
                return (
                    f"Great! Based on your requirement of ₹{sales_output.requested_amount:,} "
                    f"for {sales_output.tenure_months} months ({sales_output.tenure_months // 12} years), "
                    f"your estimated EMI would be around ₹{sales_output.estimated_emi:,.2f} "
                    f"at an interest rate in the range of {sales_output.interest_range}.\n\n"
                    f"Now, let's proceed with KYC verification. Please provide:\n"
                    f"1. Your full name\n"
                    f"2. Your PAN number\n"
                    f"3. Your employment type (SALARIED/SELF_EMPLOYED/BUSINESS)"
                )
                
            except Exception as e:
                return f"I encountered an error processing your loan request. Please try again with the loan amount and tenure."
        
        else:
            # Need more information
            missing = []
            if "amount" not in entities:
                missing.append("loan amount")
            if "tenure_months" not in entities:
                missing.append("tenure")
            
            return f"I need a bit more information. Please provide your {' and '.join(missing)}."
    
    def _handle_kyc_stage(self, state: ConversationState, user_message: str, intent: str) -> str:
        """Handle KYC stage - verify customer details"""
        
        # Extract entities
        entities = self.llm_service.extract_entities(user_message, intent)
        
        # For simplicity, extract from message directly (in production, use better NER)
        # This is a simplified extraction - you may want to improve this
        words = user_message.split()
        
        # Try to extract name (first 2-3 words if not PAN)
        name = None
        pan = entities.get("pan")
        employment_type = None
        
        # Simple heuristics for extraction
        for word in words:
            if word.upper() in ["SALARIED", "SELF_EMPLOYED", "BUSINESS"]:
                employment_type = word.upper()
                break
            if "EMPLOYED" in word.upper():
                employment_type = "SELF_EMPLOYED"
                break
        
        # Extract name (assume first capitalized words before PAN)
        if not name:
            name_parts = []
            for word in words:
                if word[0].isupper() and len(word) > 1 and not word.isupper():
                    name_parts.append(word)
                if len(name_parts) >= 2:
                    break
            if name_parts:
                name = " ".join(name_parts)
        
        # Check if we have all required info
        if name and pan and employment_type:
            try:
                # Call Verification Agent
                verification_output = self.verification_agent.run(
                    input_data={
                        "name": name,
                        "pan": pan,
                        "employment_type": employment_type
                    },
                    context={"session_id": state.session_id}
                )
                
                # Check KYC status
                if verification_output.kyc_status == KYCStatus.FAILED:
                    self._transition_stage(state, ConversationStage.FAILED, "KYC verification failed")
                    return (
                        f"I'm sorry, but we couldn't verify your details. "
                        f"Issues found: {', '.join(verification_output.risk_flags)}. "
                        f"Please contact our support team for assistance."
                    )
                
                # Update state with KYC data and customer info
                state.kyc_data = verification_output
                state.customer_id = self.verification_agent.crm_service.lookup_by_pan(pan)["customer_id"]
                state.customer_name = name
                self.state_manager.save_state(state)
                
                # Transition to Underwriting
                self._transition_stage(state, ConversationStage.UNDERWRITING, "KYC verified")
                
                # Automatically trigger underwriting
                return self._handle_underwriting_stage(state)
                
            except Exception as e:
                return "I encountered an error during verification. Please provide your name, PAN, and employment type again."
        
        else:
            return (
                "Please provide all required details:\n"
                "- Your full name\n"
                "- Your PAN number (format: ABCDE1234F)\n"
                "- Employment type (SALARIED/SELF_EMPLOYED/BUSINESS)"
            )
    
    def _handle_underwriting_stage(self, state: ConversationState) -> str:
        """Handle UNDERWRITING stage - automatic credit decisioning"""
        
        if not state.sales_data or not state.kyc_data:
            return "Error: Missing sales or KYC data."
        
        try:
            # Call Underwriting Agent
            underwriting_output = self.underwriting_agent.run(
                input_data={
                    "customer_id": state.customer_id,
                    "requested_amount": state.sales_data.requested_amount,
                    "tenure_months": state.sales_data.tenure_months,
                    "monthly_income": state.kyc_data.monthly_income,
                    "estimated_emi": state.sales_data.estimated_emi
                },
                context={"session_id": state.session_id}
            )
            
            # Update state
            state.underwriting_data = underwriting_output
            self.state_manager.save_state(state)
            
            # Handle decision
            if underwriting_output.decision == UnderwritingDecision.REJECTED:
                self._transition_stage(state, ConversationStage.FAILED, "Loan rejected")
                return (
                    f"We regret to inform you that your loan application could not be approved at this time. "
                    f"Your credit score is {underwriting_output.credit_score}. "
                    f"Please contact our support team for more information."
                )
            
            elif underwriting_output.decision == UnderwritingDecision.CONDITIONAL:
                # Transition to Sanction with modified amount
                self._transition_stage(state, ConversationStage.SANCTION, "Conditional approval")
                
                # Explain the decision
                rate_explanation = self._explain_interest_rate(underwriting_output.rate_components)
                
                response = (
                    f"Good news! Your loan has been conditionally approved.\n\n"
                    f"📊 Credit Score: {underwriting_output.credit_score} (Risk Grade: {underwriting_output.risk_grade})\n"
                    f"💰 Approved Amount: ₹{underwriting_output.approved_amount:,} "
                    f"(Modified from requested ₹{state.sales_data.requested_amount:,})\n"
                    f"📈 Interest Rate: {underwriting_output.final_interest_rate}% per annum\n"
                    f"{rate_explanation}\n\n"
                    f"Generating your sanction letter..."
                )
                
                # Automatically trigger sanction letter generation
                sanction_response = self._handle_sanction_stage(state)
                return response + "\n\n" + sanction_response
            
            else:  # APPROVED
                self._transition_stage(state, ConversationStage.SANCTION, "Loan approved")
                
                # Explain the decision
                rate_explanation = self._explain_interest_rate(underwriting_output.rate_components)
                
                response = (
                    f"🎉 Congratulations! Your loan has been approved!\n\n"
                    f"📊 Credit Score: {underwriting_output.credit_score} (Risk Grade: {underwriting_output.risk_grade})\n"
                    f"💰 Approved Amount: ₹{underwriting_output.approved_amount:,}\n"
                    f"📈 Interest Rate: {underwriting_output.final_interest_rate}% per annum\n"
                    f"{rate_explanation}\n\n"
                    f"Generating your sanction letter..."
                )
                
                # Automatically trigger sanction letter generation
                sanction_response = self._handle_sanction_stage(state)
                return response + "\n\n" + sanction_response
        
        except Exception as e:
            return f"Error during underwriting: {str(e)}"
    
    def _handle_sanction_stage(self, state: ConversationState) -> str:
        """Handle SANCTION stage - generate sanction letter"""
        
        if not state.underwriting_data:
            return "Error: Missing underwriting data."
        
        try:
            # Recalculate EMI with final approved amount and rate
            from utils.emi_calculator import calculate_emi
            final_emi = calculate_emi(
                state.underwriting_data.approved_amount,
                state.underwriting_data.final_interest_rate,
                state.sales_data.tenure_months
            )
            
            # Call Sanction Agent
            sanction_output = self.sanction_agent.run(
                input_data={
                    "session_id": state.session_id,
                    "customer_name": state.customer_name,
                    "customer_id": state.customer_id,
                    "approved_amount": state.underwriting_data.approved_amount,
                    "tenure_months": state.sales_data.tenure_months,
                    "final_interest_rate": state.underwriting_data.final_interest_rate,
                    "estimated_emi": final_emi,
                    "risk_grade": state.underwriting_data.risk_grade
                },
                context={"session_id": state.session_id}
            )
            
            # Update state
            state.sanction_letter_path = sanction_output.letter_path
            self.state_manager.save_state(state)
            
            # Transition to Completed
            self._transition_stage(state, ConversationStage.COMPLETED, "Sanction letter generated")
            
            return (
                f"✅ Your sanction letter has been generated successfully!\n\n"
                f"📄 Sanction ID: {sanction_output.sanction_id}\n"
                f"📁 Letter saved at: {sanction_output.letter_path}\n"
                f"⏰ Valid for: {sanction_output.validity_days} days\n\n"
                f"Final EMI: ₹{final_emi:,.2f} per month\n\n"
                f"Thank you for choosing BFSI Bank! Please download your sanction letter and "
                f"contact our loan officer to proceed with documentation."
            )
        
        except Exception as e:
            return f"Error generating sanction letter: {str(e)}"
    
    def _handle_unclear_intent(self, state: ConversationState, user_message: str) -> str:
        """Handle cases where intent confidence is low"""
        
        if state.current_stage == ConversationStage.SALES:
            return (
                "I didn't quite catch that. Could you please tell me:\n"
                "- The loan amount you need (e.g., '5 lakhs')\n"
                "- The tenure you prefer (e.g., '3 years')"
            )
        
        elif state.current_stage == ConversationStage.KYC:
            return (
                "I need your KYC details to proceed. Please provide:\n"
                "- Your full name\n"
                "- Your PAN number\n"
                "- Your employment type (SALARIED/SELF_EMPLOYED/BUSINESS)"
            )
        
        return "I'm not sure I understood. Could you please rephrase?"
    
    def _transition_stage(self, state: ConversationState, new_stage: ConversationStage, reason: str) -> None:
        """Transition to a new conversation stage"""
        old_stage = state.current_stage
        state.current_stage = new_stage
        self.state_manager.save_state(state)
        
        # Log transition
        self.audit_logger.log_state_transition(
            session_id=state.session_id,
            from_stage=old_stage,
            to_stage=new_stage,
            reason=reason
        )
    
    def _explain_interest_rate(self, rate_components: Dict[str, float]) -> str:
        """Generate customer-friendly explanation of interest rate calculation"""
        base = rate_components.get("base", 11.0)
        credit_adj = rate_components.get("credit_adjustment", 0.0)
        tenure_adj = rate_components.get("tenure_adjustment", 0.0)
        
        explanation = f"   Rate Breakdown: Base {base}%"
        
        if credit_adj != 0:
            sign = "+" if credit_adj > 0 else ""
            explanation += f" {sign}{credit_adj}% (credit score adjustment)"
        
        if tenure_adj != 0:
            explanation += f" +{tenure_adj}% (tenure adjustment)"
        
        return explanation
    
    def get_session_summary(self) -> Dict:
        """Get summary of current session"""
        if not self.current_session_id:
            return {}
        
        return self.state_manager.get_session_summary(self.current_session_id)
