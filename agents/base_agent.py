"""Base agent interface for all worker agents"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from datetime import datetime

from services.audit_logger import AuditLogger


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    Enforces consistent interface and audit logging.
    """
    
    def __init__(self, audit_logger: AuditLogger):
        """
        Initialize base agent with audit logger
        
        Args:
            audit_logger: Audit logger instance for tracking executions
        """
        self.audit_logger = audit_logger
        self.agent_name = self.__class__.__name__
    
    @abstractmethod
    def execute(self, input_data: Any, context: Dict) -> Any:
        """
        Execute agent logic and return structured output
        
        Args:
            input_data: Structured input (Pydantic model or dict)
            context: Additional context (session_id, etc.)
        
        Returns:
            Structured output (Pydantic model)
        """
        pass
    
    def run(self, input_data: Any, context: Dict) -> Any:
        """
        Wrapper method that executes agent and logs to audit trail
        
        Args:
            input_data: Input data for the agent
            context: Execution context
        
        Returns:
            Agent output
        """
        session_id = context.get("session_id", "unknown")
        start_time = datetime.now()
        
        try:
            # Execute agent logic
            output = self.execute(input_data, context)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log successful execution
            self.log_execution(
                session_id=session_id,
                input_data=input_data,
                output_data=output,
                success=True,
                execution_time_ms=execution_time
            )
            
            return output
            
        except Exception as e:
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log failed execution
            self.log_execution(
                session_id=session_id,
                input_data=input_data,
                output_data=None,
                success=False,
                execution_time_ms=execution_time,
                error_message=str(e)
            )
            
            raise
    
    def log_execution(
        self,
        session_id: str,
        input_data: Any,
        output_data: Any,
        success: bool = True,
        execution_time_ms: float = None,
        error_message: str = None
    ) -> None:
        """
        Log agent execution to audit trail
        
        Args:
            session_id: Session identifier
            input_data: Input provided to agent
            output_data: Output from agent
            success: Whether execution was successful
            execution_time_ms: Execution time in milliseconds
            error_message: Error message if failed
        """
        self.audit_logger.log_execution(
            session_id=session_id,
            agent_name=self.agent_name,
            input_data=input_data,
            output_data=output_data,
            success=success,
            execution_time_ms=execution_time_ms,
            error_message=error_message
        )
