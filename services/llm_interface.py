import re
import json
from typing import List, Dict, Optional
from models.agent_io import IntentDetectionResult
from models.state import Message
from models.enums import ConversationStage


class LLMService:
    """
    LLM service for intent detection with confidence scoring.
    Uses Ollama for intelligent intent detection with fallback to rule-based matching.
    """
    
    # Confidence threshold for accepting an intent
    CONFIDENCE_THRESHOLD = 0.7
    
    # Ollama configuration
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "mistral"  # Use the model you have installed (check with: ollama list)
    USE_OLLAMA = False  # Set to True to enable Ollama (slower but handles natural language better)
    
    def __init__(self):
        """Initialize LLM service and check Ollama availability"""
        self.ollama_available = self._check_ollama_availability() if self.USE_OLLAMA else False
        
        # Only show status if Ollama is enabled
        if self.USE_OLLAMA:
            if self.ollama_available:
                print(f"✓ Ollama detected - using {self.OLLAMA_MODEL} for intent detection")
            else:
                print("⚠ Ollama enabled but not available - using rule-based intent detection")
    
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            import requests
            response = requests.get(f"{self.OLLAMA_BASE_URL}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    # Stage-compatible intents mapping
    STAGE_INTENTS = {
        ConversationStage.SALES: [
            "provide_loan_amount",
            "provide_tenure",
            "confirm_loan_details",
            "modify_loan_request"
        ],
        ConversationStage.KYC: [
            "provide_pan",
            "provide_employment",
            "provide_income",
            "confirm_kyc"
        ],
        ConversationStage.UNDERWRITING: [],  # System-driven, no user intents
        ConversationStage.SANCTION: [
            "download_letter",
            "accept_offer",
            "request_modification"
        ]
    }
    
    # Keyword patterns for intent detection
    INTENT_PATTERNS = {
        "provide_loan_amount": [
            r'\b(\d+)\s*(?:lakh|lakhs|l)\b',  # "5 lakhs" or "5lakh"
            r'\b(\d{1,2}[,\s]?\d{2}[,\s]?\d{3})\s*(?:rs|rupees)?\b',  # "7,00,000" or "700000"
            r'\bneed\s+(?:a\s+)?loan\s+of\b',
            r'\bwant\s+(?:a\s+)?loan\s+of\b',
            r'\bget\s+(?:a\s+)?loan\b'
        ],
        "provide_tenure": [
            r'\b(\d+)\s*(?:year|years|yr|yrs)\b',  # "4 years" or "4years"
            r'\b(\d+)\s*(?:month|months)\b',
            r'\bfor\s+(\d+)\s*(?:year|years|yr|yrs)\b',
            r'\btenure\s+of\s+(\d+)\b'
        ],
        "confirm_loan_details": [
            r'\byes\b',
            r'\bconfirm\b',
            r'\bok\b',
            r'\bagree\b',
            r'\bproceed\b'
        ],
        "provide_pan": [
            r'\b[A-Z]{5}\d{4}[A-Z]\b',  # PAN format
            r'\bpan\s+(?:is\s+)?[A-Z]{5}\d{4}[A-Z]\b'
        ],
        "provide_employment": [
            r'\bsalaried\b',
            r'\bself[- ]employed\b',
            r'\bbusiness\b',
            r'\bwork\s+(?:at|for|in)\b'
        ],
        "provide_income": [
            r'\b(?:salary|income)\s+(?:is\s+)?(\d+)\b',
            r'\bearn\s+(\d+)\b',
            r'\b(\d+)\s+per\s+month\b'
        ],
        "download_letter": [
            r'\bdownload\b',
            r'\bget\s+(?:the\s+)?letter\b',
            r'\bsend\s+(?:me\s+)?(?:the\s+)?letter\b'
        ],
        "accept_offer": [
            r'\baccept\b',
            r'\bagree\b',
            r'\byes\b',
            r'\bproceed\b'
        ]
    }
    
    
    def detect_intent(
        self,
        user_message: str,
        current_stage: ConversationStage,
        conversation_history: List[Message]
    ) -> IntentDetectionResult:
        """
        Detect user intent with confidence scoring.
        Uses Ollama if available, otherwise falls back to rule-based matching.
        
        Args:
            user_message: The user's input message
            current_stage: Current conversation stage
            conversation_history: Previous messages for context
        
        Returns:
            IntentDetectionResult with intent, confidence, and clarification flag
        """
        # Try Ollama first if available
        if self.ollama_available:
            try:
                return self._detect_intent_with_ollama(user_message, current_stage, conversation_history)
            except Exception as e:
                print(f"⚠ Ollama failed: {e}, falling back to rule-based")
                # Fall through to rule-based
        
        # Fallback to rule-based matching
        return self._detect_intent_rule_based(user_message, current_stage)
    
    def _detect_intent_with_ollama(
        self,
        user_message: str,
        current_stage: ConversationStage,
        conversation_history: List[Message]
    ) -> IntentDetectionResult:
        """Use Ollama to detect intent with LLM reasoning"""
        import requests
        
        # Get valid intents for current stage
        valid_intents = self.STAGE_INTENTS.get(current_stage, [])
        
        if not valid_intents:
            return IntentDetectionResult(
                intent="none",
                confidence=1.0,
                requires_clarification=False
            )
        
        # Build context from conversation history
        context = "\n".join([
            f"{msg.role}: {msg.content}" 
            for msg in conversation_history[-3:]  # Last 3 messages for context
        ])
        
        # Construct prompt for Ollama
        prompt = f"""You are an intent classifier for a loan application system.

Current Stage: {current_stage}
Valid Intents: {', '.join(valid_intents)}

Conversation Context:
{context}

User Message: "{user_message}"

Task: Classify the user's intent and provide a confidence score (0.0 to 1.0).

Respond ONLY with valid JSON in this exact format:
{{"intent": "one_of_valid_intents", "confidence": 0.95}}

If the message doesn't match any valid intent, use:
{{"intent": "unknown", "confidence": 0.0}}

JSON Response:"""
        
        # Call Ollama API
        response = requests.post(
            f"{self.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": self.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent classification
                    "num_predict": 100
                }
            },
            timeout=10
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.status_code}")
        
        # Parse Ollama response
        ollama_output = response.json()
        llm_response = ollama_output.get("response", "").strip()
        
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\{[^}]+\}', llm_response)
        if json_match:
            result = json.loads(json_match.group())
            intent = result.get("intent", "unknown")
            confidence = float(result.get("confidence", 0.0))
            
            # Validate intent is in valid list
            if intent not in valid_intents and intent != "unknown":
                intent = "unknown"
                confidence = 0.0
            
            return IntentDetectionResult(
                intent=intent,
                confidence=confidence,
                requires_clarification=confidence < self.CONFIDENCE_THRESHOLD
            )
        
        # If JSON parsing fails, fall back to rule-based
        raise Exception("Failed to parse Ollama response")
    
    def _detect_intent_rule_based(
        self,
        user_message: str,
        current_stage: ConversationStage
    ) -> IntentDetectionResult:
        """Rule-based intent detection (fallback method)"""
        user_message_lower = user_message.lower()
        
        # Get valid intents for current stage
        valid_intents = self.STAGE_INTENTS.get(current_stage, [])
        
        if not valid_intents:
            # Stage is system-driven (e.g., UNDERWRITING)
            return IntentDetectionResult(
                intent="none",
                confidence=1.0,
                requires_clarification=False
            )
        
        # Score each valid intent
        intent_scores = {}
        for intent in valid_intents:
            score = self._calculate_intent_score(user_message_lower, intent)
            if score > 0:
                intent_scores[intent] = score
        
        # No matching intent found
        if not intent_scores:
            return IntentDetectionResult(
                intent="unknown",
                confidence=0.0,
                requires_clarification=True
            )
        
        # Get best matching intent
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent], 1.0)
        
        return IntentDetectionResult(
            intent=best_intent,
            confidence=confidence,
            requires_clarification=confidence < self.CONFIDENCE_THRESHOLD
        )
    
    def _calculate_intent_score(self, message: str, intent: str) -> float:
        """Calculate confidence score for a specific intent"""
        patterns = self.INTENT_PATTERNS.get(intent, [])
        
        if not patterns:
            return 0.0
        
        matches = 0
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                matches += 1
        
        # Confidence based on pattern match ratio
        confidence = matches / len(patterns)
        
        # Boost confidence if multiple patterns match
        if matches > 1:
            confidence = min(confidence * 1.5, 1.0)
        
        return confidence
    
    def extract_entities(self, user_message: str, intent: str) -> Dict:
        """Extract entities from user message based on intent"""
        entities = {}
        
        if intent == "provide_loan_amount":
            # Extract amount in lakhs (handle "7lakh", "7 lakhs", "7L")
            match = re.search(r'(\d+)\s*(?:lakh|lakhs|l)\b', user_message, re.IGNORECASE)
            if match:
                entities['amount'] = int(match.group(1)) * 100000
            else:
                # Try to extract raw numbers like "700000" or "7,00,000"
                match = re.search(r'(\d{1,2})[,\s]?(\d{2})[,\s]?(\d{3})', user_message)
                if match:
                    amount_str = match.group(1) + match.group(2) + match.group(3)
                    entities['amount'] = int(amount_str)
            
            # Also try to extract tenure from the same message
            tenure_match = re.search(r'(\d+)\s*(?:year|years|yr|yrs)\b', user_message, re.IGNORECASE)
            if tenure_match:
                entities['tenure_months'] = int(tenure_match.group(1)) * 12
        
        elif intent == "provide_tenure":
            # Extract tenure in months (handle "4years", "4 years")
            match = re.search(r'(\d+)\s*(?:year|years|yr|yrs)\b', user_message, re.IGNORECASE)
            if match:
                entities['tenure_months'] = int(match.group(1)) * 12
            else:
                match = re.search(r'(\d+)\s*(?:month|months)\b', user_message, re.IGNORECASE)
                if match:
                    entities['tenure_months'] = int(match.group(1))
            
            # Also try to extract amount from the same message
            amount_match = re.search(r'(\d+)\s*(?:lakh|lakhs|l)\b', user_message, re.IGNORECASE)
            if amount_match:
                entities['amount'] = int(amount_match.group(1)) * 100000
        
        elif intent == "provide_pan":
            # Extract PAN
            match = re.search(r'\b([A-Z]{5}\d{4}[A-Z])\b', user_message)
            if match:
                entities['pan'] = match.group(1)
        
        elif intent == "provide_income":
            # Extract income
            match = re.search(r'(\d+)', user_message)
            if match:
                entities['monthly_income'] = int(match.group(1))
        
        return entities
