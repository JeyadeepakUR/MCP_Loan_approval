"""Main entry point for the loan origination system"""
from agents.master_agent import MasterAgent


def main():
    """Interactive CLI for loan origination conversation"""
    print("=" * 60)
    print("BFSI BANK - PERSONAL LOAN ORIGINATION SYSTEM")
    print("=" * 60)
    print()
    
    # Initialize Master Agent
    master = MasterAgent()
    
    # Start conversation
    welcome = master.start_conversation()
    print(f"System: {welcome}\n")
    
    # Conversation loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Exit commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nThank you for using BFSI Bank services. Goodbye!")
                
                # Print session summary
                summary = master.get_session_summary()
                if summary:
                    print("\n" + "=" * 60)
                    print("SESSION SUMMARY")
                    print("=" * 60)
                    print(f"Session ID: {summary.get('session_id')}")
                    print(f"Current Stage: {summary.get('current_stage')}")
                    print(f"Customer ID: {summary.get('customer_id', 'N/A')}")
                    print(f"Messages Exchanged: {summary.get('message_count')}")
                    print(f"Sanction Letter: {'Generated' if summary.get('sanction_letter_generated') else 'Not Generated'}")
                    print("=" * 60)
                
                break
            
            # Process message
            response = master.process_message(user_input)
            print(f"\nSystem: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nConversation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    main()
