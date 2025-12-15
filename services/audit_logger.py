import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class AuditLogger:
    """Append-only audit logger for tracking all agent executions"""
    
    def __init__(self, data_dir: str = "data/audit"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def log_execution(
        self,
        session_id: str,
        agent_name: str,
        input_data: Any,
        output_data: Any,
        success: bool = True,
        execution_time_ms: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Log an agent execution to the audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "agent": agent_name,
            "input": self._serialize(input_data),
            "output": self._serialize(output_data),
            "metadata": {
                "success": success,
                "execution_time_ms": execution_time_ms,
                "error": error_message
            }
        }
        
        log_file = self.data_dir / f"{session_id}.jsonl"
        
        # Append-only write
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, default=str) + '\n')
    
    def log_state_transition(
        self,
        session_id: str,
        from_stage: str,
        to_stage: str,
        reason: str
    ) -> None:
        """Log a state transition"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "event_type": "STATE_TRANSITION",
            "from_stage": from_stage,
            "to_stage": to_stage,
            "reason": reason
        }
        
        log_file = self.data_dir / f"{session_id}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, default=str) + '\n')
    
    def get_audit_trail(self, session_id: str) -> list:
        """Retrieve complete audit trail for a session"""
        log_file = self.data_dir / f"{session_id}.jsonl"
        
        if not log_file.exists():
            return []
        
        audit_trail = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    audit_trail.append(json.loads(line))
        
        return audit_trail
    
    def _serialize(self, data: Any) -> Any:
        """Serialize data for logging"""
        if hasattr(data, 'model_dump'):
            return data.model_dump(mode='json')
        elif isinstance(data, dict):
            return data
        elif isinstance(data, (list, tuple)):
            return [self._serialize(item) for item in data]
        else:
            return str(data)
