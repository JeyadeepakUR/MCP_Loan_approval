"""Failure case examples - Various rejection scenarios"""
from agents.master_agent import MasterAgent


def run_low_credit_score_rejection():
    """Scenario: Customer with low credit score gets rejected"""
    print("=" * 80)
    print("FAILURE CASE 1: Low Credit Score Rejection")
    print("=" * 80)
    print()
    
    master = MasterAgent()
    
    welcome = master.start_conversation()
    print(f"System: {welcome}\n")
    print("-" * 80)
    
    # Customer: Meera Nair (CUST010) - will have lower credit score
    conversations = [
        ("I need 3 lakhs for 2 years", "Loan request"),
        ("Meera Nair, PAN YZABC8901D, SALARIED", "KYC details"),
    ]
    
    for user_msg, description in conversations:
        print(f"\n[{description}]")
        print(f"Customer: {user_msg}\n")
        response = master.process_message(user_msg)
        print(f"System: {response}\n")
        print("-" * 80)
    
    print(f"\nFinal Stage: {master.state_manager.load_state(master.current_session_id).current_stage}")
    print("=" * 80)


def run_high_emi_rejection():
    """Scenario: EMI exceeds 50% of income"""
    print("\n\n" + "=" * 80)
    print("FAILURE CASE 2: High EMI-to-Income Ratio Rejection")
    print("=" * 80)
    print()
    
    master = MasterAgent()
    
    welcome = master.start_conversation()
    print(f"System: {welcome}\n")
    print("-" * 80)
    
    # Customer: Anita Desai (CUST006) - income 45,000, requesting high amount
    conversations = [
        ("I need 15 lakhs for 5 years", "High loan request"),
        ("Anita Desai, PAN BCDEF2345G, SALARIED", "KYC details"),
    ]
    
    for user_msg, description in conversations:
        print(f"\n[{description}]")
        print(f"Customer: {user_msg}\n")
        response = master.process_message(user_msg)
        print(f"System: {response}\n")
        print("-" * 80)
    
    print(f"\nFinal Stage: {master.state_manager.load_state(master.current_session_id).current_stage}")
    print("=" * 80)


def run_kyc_failure():
    """Scenario: KYC verification fails"""
    print("\n\n" + "=" * 80)
    print("FAILURE CASE 3: KYC Verification Failure")
    print("=" * 80)
    print()
    
    master = MasterAgent()
    
    welcome = master.start_conversation()
    print(f"System: {welcome}\n")
    print("-" * 80)
    
    # Invalid PAN
    conversations = [
        ("I need 5 lakhs for 3 years", "Loan request"),
        ("John Doe, PAN INVALID123, SALARIED", "Invalid PAN"),
    ]
    
    for user_msg, description in conversations:
        print(f"\n[{description}]")
        print(f"Customer: {user_msg}\n")
        response = master.process_message(user_msg)
        print(f"System: {response}\n")
        print("-" * 80)
    
    print(f"\nFinal Stage: {master.state_manager.load_state(master.current_session_id).current_stage}")
    print("=" * 80)


def run_conditional_approval():
    """Scenario: Conditional approval with reduced amount"""
    print("\n\n" + "=" * 80)
    print("SUCCESS CASE: Conditional Approval (Reduced Amount)")
    print("=" * 80)
    print()
    
    master = MasterAgent()
    
    welcome = master.start_conversation()
    print(f"System: {welcome}\n")
    print("-" * 80)
    
    # Customer: Sneha Reddy (CUST004) - income 55,000, requesting high amount
    conversations = [
        ("I need 12 lakhs for 4 years", "High loan request"),
        ("Sneha Reddy, PAN QRSTU3456V, SALARIED", "KYC details"),
    ]
    
    for user_msg, description in conversations:
        print(f"\n[{description}]")
        print(f"Customer: {user_msg}\n")
        response = master.process_message(user_msg)
        print(f"System: {response}\n")
        print("-" * 80)
    
    print(f"\nFinal Stage: {master.state_manager.load_state(master.current_session_id).current_stage}")
    print("=" * 80)


if __name__ == "__main__":
    run_low_credit_score_rejection()
    run_high_emi_rejection()
    run_kyc_failure()
    run_conditional_approval()
