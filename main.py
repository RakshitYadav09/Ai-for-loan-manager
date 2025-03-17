# main.py
import os
from dotenv import load_dotenv
from voice_interaction import VoiceBasedChatbot

def main():
    # Load environment variables
    load_dotenv()
    
    print("Starting AI Loan Manager...")
    
    # Create chatbot
    chatbot = VoiceBasedChatbot()
    
    # Start conversation
    try:
        chatbot.start_conversation()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    
    print("Application session ended.")

if __name__ == "__main__":
    main()
