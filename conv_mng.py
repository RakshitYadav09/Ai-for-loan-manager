# conversation_manager.py
from gemini_integration import GeminiAI
from loan_eligibility import LoanEligibilityEngine
import json
from datetime import datetime
import sys
import time
import websocket

class TextBasedConversationManager:
    def __init__(self):
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

        # Print the report to the terminal
        print(final_report)
        self.send_message(final_report)

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
            message = f"\nLoan eligibility report saved to {file_path}"
            print(message)
            self.send_message(message)
            return report
        except Exception as e:
            error_message = f"Error saving report: {e}"
            print(error_message)
            self.send_message(error_message)
            return None

    def display_report(self):
        """Generate and display the current report"""
        print("\n=== GENERATING LOAN ELIGIBILITY REPORT ===\n")
        self.send_message("\n=== GENERATING LOAN ELIGIBILITY REPORT ===\n")
        
        report = self.generate_json_report()
        
        # Display a formatted version of the report
        print("\n=== LOAN APPLICATION REPORT ===\n")
        self.send_message("\n=== LOAN APPLICATION REPORT ===\n")
        
        # Display applicant data
        print("APPLICANT INFORMATION:")
        self.send_message("APPLICANT INFORMATION:")
        
        # Personal information
        personal = report["applicant_data"].get("personal_information", {})
        if personal:
            print("\nPersonal Details:")
            self.send_message("\nPersonal Details:")
            for key, value in personal.items():
                info = f"  {key.replace('_', ' ').title()}: {value}"
                print(info)
                self.send_message(info)
        
        # Employment information
        employment = report["applicant_data"].get("employment", {})
        if employment:
            print("\nEmployment Details:")
            self.send_message("\nEmployment Details:")
            for key, value in employment.items():
                info = f"  {key.replace('_', ' ').title()}: {value}"
                print(info)
                self.send_message(info)
        
        # Financial information
        financial = report["applicant_data"].get("financial", {})
        if financial:
            print("\nFinancial Details:")
            self.send_message("\nFinancial Details:")
            for key, value in financial.items():
                info = f"  {key.replace('_', ' ').title()}: {value}"
                print(info)
                self.send_message(info)
        
        # Loan request details
        loan_request = report["applicant_data"].get("loan_request", {})
        if loan_request:
            print("\nLoan Request Details:")
            self.send_message("\nLoan Request Details:")
            for key, value in loan_request.items():
                info = f"  {key.replace('_', ' ').title()}: {value}"
                print(info)
                self.send_message(info)
        
        # Eligibility assessment
        print("\nELIGIBILITY ASSESSMENT:")
        self.send_message("\nELIGIBILITY ASSESSMENT:")
        status = f"  Status: {report['eligibility_assessment']['status']}"
        print(status)
        self.send_message(status)
        
        if report['eligibility_assessment'].get('factors'):
            print("\nFactors:")
            self.send_message("\nFactors:")
            for factor in report['eligibility_assessment']['factors']:
                factor_info = f"  - {factor}"
                print(factor_info)
                self.send_message(factor_info)
        
        if report['eligibility_assessment'].get('recommendations'):
            print("\nRecommendations:")
            self.send_message("\nRecommendations:")
            for recommendation in report['eligibility_assessment']['recommendations']:
                rec_info = f"  - {recommendation}"
                print(rec_info)
                self.send_message(rec_info)
        
        report_date = f"\nReport generated on: {report['report_date']}"
        print(report_date)
        self.send_message(report_date)
        print("\n===============================\n")
        self.send_message("\n===============================\n")
        
        # Text summary
        summary = f"Report generated. Your loan application status is: {report['eligibility_assessment']['status']}."
        self.send_message(summary)
        
        return report

    def send_message(self, msg):
        """Send message to WebSocket."""
        try:
            if hasattr(self, 'ws') and self.ws.connected:
                self.ws.send(json.dumps({"message": msg}))
        except Exception as e:
            print(f"WebSocket send error: {e}")

    def start_conversation(self):
        """Start the conversation"""
        # Setup WebSocket connection
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect("ws://localhost:5001")
        except Exception as e:
            print("WebSocket connection failed:", e)
            self.ws = None
        
        welcome_message = "Hello! I'm your AI loan assistant. Let's start your loan application."
        print(welcome_message)
        self.send_message(welcome_message)
        
        question_count = 0

        while question_count < self.max_questions:
            # Get next question from Gemini
            recent_history = "\n".join(self.conversation_history[-6:]) if self.conversation_history else ""
            next_question = self.ai.get_next_question(self.applicant_data, recent_history)

            # Ask the question and get user response
            print(next_question)
            self.send_message(next_question)
            
            # Get text input from user
            user_response = input("> ")

            if not user_response.strip():
                response_message = "I didn't get any input. Could you please type your response?"
                print(response_message)
                self.send_message(response_message)
                continue

            # Check for commands
            if user_response.lower() in ["exit", "quit", "stop"]:
                exit_message = "Thank you for using our service. I'll generate a report with the information provided so far."
                print(exit_message)
                self.send_message(exit_message)
                self.save_json_report()
                goodbye_message = "Goodbye!"
                print(goodbye_message)
                self.send_message(goodbye_message)
                break
            
            # Check for generate command
            if user_response.lower() in ["generate", "report", "show report", "generate report"]:
                report_message = "Generating your loan eligibility report now."
                print(report_message)
                self.send_message(report_message)
                self.display_report()
                continue

            # Process response with Gemini
            response_data = self.ai.handle_user_response(user_response, self.applicant_data)
            
            # Update applicant data or ask for clarification
            if response_data.get("needs_clarification"):
                clarification_question = response_data["clarification_question"]
                print(clarification_question)
                self.send_message(clarification_question)
                clarification_response = input("> ")
                
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
            report_message = "\nGenerating your loan eligibility report..."
            print(report_message)
            self.send_message(report_message)
            
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
                self.send_message(missing_info_report)
                
                print("\nMissing Information Report:")
                self.send_message("\nMissing Information Report:")
            
            else:
                # If all data is complete, provide a full assessment
                complete_message = "\nAll required information has been collected."
                print(complete_message)
                self.send_message(complete_message)
                
                report_header = "\nFinal Report:\n"
                print(report_header)
                self.send_message(report_header)
                self.provide_final_assessment()

        self.save_json_report()  # Save the report at the end of the conversation
        
        # Close WebSocket connection
        if hasattr(self, 'ws') and self.ws:
            self.ws.close()

# Main execution
if __name__ == "__main__":
    manager = TextBasedConversationManager()
    manager.start_conversation()