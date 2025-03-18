# conversation_manager.py
from voice_interaction import VoiceBasedChatbot
from gemini_integration import GeminiAI
from loan_eligibility import LoanEligibilityEngine
import json
from datetime import datetime

class DynamicConversationManager:
    def __init__(self):
        self.voice = VoiceBasedChatbot()
        self.ai = GeminiAI()
        self.eligibility_engine = LoanEligibilityEngine()
        self.applicant_data = self.load_applicant_data()
        self.conversation_history = []
        self.max_questions = 3  # Limit to 3 questions

    def load_applicant_data(self, file_path='applicant_data.json'):
        """Load applicant data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {
                "personal_information": {},
                "identification": {},
                "employment": {},
                "financial": {},
                "loan_request": {}
            }

    def save_applicant_data(self, file_path='applicant_data.json'):
        """Save updated applicant data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.applicant_data, file, indent=2)

    def update_applicant_data(self, updates):
        """Update applicant data with new information"""
        for category, details in updates.items():
            if category not in self.applicant_data:
                self.applicant_data[category] = {}
            for key, value in details.items():
                self.applicant_data[category][key] = value

    def is_data_complete(self):
        """Check if all required data has been collected"""
        required_fields = [
            self.applicant_data.get('financial', {}).get('credit_score'),
            self.applicant_data.get('employment', {}).get('net_monthly_salary'),
            self.applicant_data.get('financial', {}).get('monthly_expenses'),
            self.applicant_data.get('employment', {}).get('work_experience'),
            self.applicant_data.get('loan_request', {}).get('loan_amount'),
            self.applicant_data.get('loan_request', {}).get('loan_term'),
            self.applicant_data.get('loan_request', {}).get('interest_rate'),
            self.applicant_data.get('loan_request', {}).get('property_value')
        ]
        return all(required_fields)

    def provide_final_assessment(self):
        """Provide final loan eligibility assessment"""
        eligibility_result = self.eligibility_engine.check_eligibility(self.applicant_data)
        gemini_assessment = self.ai.assess_loan_eligibility(self.applicant_data)

        # Prepare final report
        final_report = f"Loan Eligibility Report:\n\n{gemini_assessment}\n"
        
        if eligibility_result["status"] == "APPROVED":
            final_report += "\nCongratulations! Your loan application has been approved."
        elif eligibility_result["status"] == "CONDITIONALLY APPROVED":
            final_report += "\nYour loan application has been conditionally approved. Here are some recommendations:"
            for recommendation in eligibility_result.get("recommendations", []):
                final_report += f"\n- {recommendation}"
        elif eligibility_result["status"] == "NEEDS_MORE_INFO":
            final_report += "\nWe need more information to complete your application:"
            for factor in eligibility_result.get("factors", []):
                final_report += f"\n- {factor}"
        else:
            final_report += "\nUnfortunately, your loan application has been rejected due to the following reasons:"
            for factor in eligibility_result.get("factors", []):
                final_report += f"\n- {factor}"

        # Print and speak the report
        print(final_report)  # Print the report to the terminal
        self.voice.speak(final_report)

    def generate_json_report(self):
        """Generate a JSON report with applicant data and eligibility assessment"""
        eligibility_result = self.eligibility_engine.check_eligibility(self.applicant_data)
        
        report = {
            "applicant_data": self.applicant_data,
            "eligibility_assessment": {
                "status": eligibility_result["status"],
                "factors": eligibility_result.get("factors", []),
                "recommendations": eligibility_result.get("recommendations", [])
            },
            "report_date": datetime.now().strftime("%B %d, %Y, %I:%M %p %Z")
        }
        
        return report

    def save_json_report(self, file_path='loan_report.json'):
        """Save the loan report to a JSON file"""
        report = self.generate_json_report()
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(report, file, indent=2)
            print(f"\nLoan eligibility report saved to {file_path}")
            return report
        except Exception as e:
            print(f"Error saving report: {e}")
            return None

    def display_report(self):
        """Generate and display the current report"""
        print("\n=== GENERATING LOAN ELIGIBILITY REPORT ===\n")
        
        report = self.generate_json_report()
        
        # Display a formatted version of the report
        print("\n=== LOAN APPLICATION REPORT ===\n")
        
        # Display applicant data
        print("APPLICANT INFORMATION:")
        
        # Personal information
        personal = report["applicant_data"].get("personal_information", {})
        if personal:
            print("\nPersonal Details:")
            for key, value in personal.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Employment information
        employment = report["applicant_data"].get("employment", {})
        if employment:
            print("\nEmployment Details:")
            for key, value in employment.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Financial information
        financial = report["applicant_data"].get("financial", {})
        if financial:
            print("\nFinancial Details:")
            for key, value in financial.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Loan request details
        loan_request = report["applicant_data"].get("loan_request", {})
        if loan_request:
            print("\nLoan Request Details:")
            for key, value in loan_request.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Eligibility assessment
        print("\nELIGIBILITY ASSESSMENT:")
        print(f"  Status: {report['eligibility_assessment']['status']}")
        
        if report['eligibility_assessment'].get('factors'):
            print("\nFactors:")
            for factor in report['eligibility_assessment']['factors']:
                print(f"  - {factor}")
        
        if report['eligibility_assessment'].get('recommendations'):
            print("\nRecommendations:")
            for recommendation in report['eligibility_assessment']['recommendations']:
                print(f"  - {recommendation}")
        
        print(f"\nReport generated on: {report['report_date']}")
        print("\n===============================\n")
        
        # Speak summary
        summary = f"Report generated. Your loan application status is: {report['eligibility_assessment']['status']}."
        self.voice.speak(summary)
        
        return report

    def start_conversation(self):
        """Start the conversation"""
        self.voice.speak("Hello! I'm your AI loan assistant. Let's start your loan application.")
        
        question_count = 0

        while question_count < self.max_questions:
            # Get next question from Gemini
            recent_history = "\n".join(self.conversation_history[-6:]) if self.conversation_history else ""
            next_question = self.ai.get_next_question(self.applicant_data, recent_history)

            # Ask the question and get user response
            self.voice.speak(next_question)
            user_response = self.voice.listen()

            if not user_response:
                self.voice.speak("I didn't catch that. Could you please repeat?")
                continue

            # Check for commands
            if user_response.lower() in ["exit", "quit", "stop"]:
                self.voice.speak("Thank you for using our service. I'll generate a report with the information provided so far.")
                self.save_json_report()
                self.voice.speak("Goodbye!")
                break
            
            # Check for generate command
            if user_response.lower() in ["generate", "report", "show report", "generate report"]:
                self.voice.speak("Generating your loan eligibility report now.")
                self.display_report()
                continue

            # Process response with Gemini
            response_data = self.ai.handle_user_response(user_response, self.applicant_data)
            
            # Update applicant data or ask for clarification
            if response_data.get("needs_clarification"):
                clarification_question = response_data["clarification_question"]
                self.voice.speak(clarification_question)
                clarification_response = self.voice.listen()
                
                if clarification_response:
                    clarification_result = self.ai.handle_user_response(clarification_response, self.applicant_data)
                    updates = clarification_result.get("data_updates", {})
                    if updates:
                        self.update_applicant_data(updates)
            
            updates = response_data.get("data_updates", {})
            if updates:
                self.update_applicant_data(updates)

            question_count += 1

        # After max questions or when data is complete, provide a report
        if question_count >= self.max_questions or self.is_data_complete():
            print("\nGenerating your loan eligibility report...")
            
            # Check completeness and provide appropriate feedback
            if not self.is_data_complete():
                missing_info_report = "Based on the information provided, we need more details to process your loan application:\n"
                
                missing_fields = []
                
                if not self.applicant_data.get('financial', {}).get('credit_score'):
                    missing_fields.append("- Credit score")
                
                if not self.applicant_data.get('employment', {}).get('net_monthly_salary'):
                    missing_fields.append("- Monthly salary")
                
                if not self.applicant_data.get('financial', {}).get('monthly_expenses'):
                    missing_fields.append("- Monthly expenses")
                
                if not self.applicant_data.get('employment', {}).get('work_experience'):
                    missing_fields.append("- Work experience")
                
                if not self.applicant_data.get('loan_request', {}).get('loan_amount'):
                    missing_fields.append("- Loan amount")
                
                if not self.applicant_data.get('loan_request', {}).get('loan_term'):
                    missing_fields.append("- Loan term")
                
                if not self.applicant_data.get('loan_request', {}).get('interest_rate'):
                    missing_fields.append("- Interest rate")
                
                if not self.applicant_data.get('loan_request', {}).get('property_value'):
                    missing_fields.append("- Property value")

                missing_info_report += "\n".join(missing_fields)
                
                print(missing_info_report)  # Print missing fields in terminal
                print("\nMissing Information Report:")
                
                # Speak missing information report
                self.voice.speak(missing_info_report)
            
            else:
                # If all data is complete, provide a full assessment
                print("\nAll required information has been collected.")
                print("\nFinal Report:")
                print("\n")
                self.provide_final_assessment()

        self.save_json_report()  # Save the report at the end of the conversation