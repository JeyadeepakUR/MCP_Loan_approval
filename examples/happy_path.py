"""Happy path example - Successful loan approval journey"""
from agents.master_agent import MasterAgent


def run_happy_path():
    """Simulate a successful loan origination conversation"""
    print("=" * 80)
    print("HAPPY PATH EXAMPLE - Successful Loan Approval")
    print("=" * 80)
    print()
    
    # Initialize Master Agent
    master = MasterAgent()
    
    # Conversation flow
    conversations = [
        ("START", None),
        ("I need a loan of 5 lakhs for 3 years", "Customer requests loan"),
        ("My name is Rajesh Kumar, PAN is ABCDE1234F, and I am SALARIED", "Customer provides KYC"),
    ]
    
    # Start conversation
    welcome = master.start_conversation()
    print(f"System: {welcome}\n")
    print("-" * 80)
    
    # Process each message
    for user_msg, description in conversations[1:]:
        print(f"\n[{description}]")
        print(f"Customer: {user_msg}\n")
        
        response = master.process_message(user_msg)
        print(f"System: {response}\n")
        print("-" * 80)
    
    # Print session summary
    print("\n" + "=" * 80)
    print("SESSION SUMMARY")
    print("=" * 80)
    summary = master.get_session_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("=" * 80)
    
    # Print audit trail
    print("\n" + "=" * 80)
    print("AUDIT TRAIL")
    print("=" * 80)
    audit_trail = master.audit_logger.get_audit_trail(master.current_session_id)
    for i, entry in enumerate(audit_trail, 1):
        print(f"\n{i}. {entry.get('event_type', entry.get('agent', 'Unknown'))}")
        if 'agent' in entry:
            print(f"   Success: {entry['metadata']['success']}")
            print(f"   Execution Time: {entry['metadata']['execution_time_ms']}ms")
    print("=" * 80)


if __name__ == "__main__":
    run_happy_path()
