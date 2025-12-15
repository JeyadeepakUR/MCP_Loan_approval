import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from filelock import FileLock

from models.state import ConversationState
from models.enums import ConversationStage


class StateManager:
    """Manages conversation state persistence with thread-safe operations"""
    
    def __init__(self, data_dir: str = "data/sessions"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def create_session(self, session_id: str) -> ConversationState:
        """Create a new conversation session"""
        state = ConversationState(
            session_id=session_id,
            current_stage=ConversationStage.SALES
        )
        self.save_state(state)
        return state
    
    def load_state(self, session_id: str) -> Optional[ConversationState]:
        """Load conversation state from file"""
        file_path = self.data_dir / f"{session_id}.json"
        
        if not file_path.exists():
            return None
        
        lock_path = self.data_dir / f"{session_id}.lock"
        with FileLock(str(lock_path)):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ConversationState(**data)
    
    def save_state(self, state: ConversationState) -> None:
        """Save conversation state to file with thread-safe locking"""
        state.updated_at = datetime.now()
        file_path = self.data_dir / f"{state.session_id}.json"
        lock_path = self.data_dir / f"{state.session_id}.lock"
        
        with FileLock(str(lock_path)):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state.model_dump(mode='json'), f, indent=2, default=str)
    
    def update_stage(self, session_id: str, new_stage: ConversationStage) -> None:
        """Update the current stage of conversation"""
        state = self.load_state(session_id)
        if state:
            state.current_stage = new_stage
            self.save_state(state)
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to conversation history"""
        from models.state import Message
        
        state = self.load_state(session_id)
        if state:
            message = Message(role=role, content=content, timestamp=datetime.now())
            state.conversation_history.append(message)
            self.save_state(state)
    
    def get_session_summary(self, session_id: str) -> dict:
        """Get a summary of the session for audit purposes"""
        state = self.load_state(session_id)
        if not state:
            return {}
        
        return {
            "session_id": state.session_id,
            "current_stage": state.current_stage,
            "customer_id": state.customer_id,
            "created_at": state.created_at.isoformat(),
            "updated_at": state.updated_at.isoformat(),
            "message_count": len(state.conversation_history),
            "has_sales_data": state.sales_data is not None,
            "has_kyc_data": state.kyc_data is not None,
            "has_underwriting_data": state.underwriting_data is not None,
            "sanction_letter_generated": state.sanction_letter_path is not None,
        }
