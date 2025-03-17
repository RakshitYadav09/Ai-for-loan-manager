import json
import os
from loan_eligibility import LoanEligibilityEngine

class LoanReportGenerator:
    def __init__(self):
        """
        Initialize the report generator
        """
        # Initialize eligibility engine
        self.eligibility_engine = LoanEligibilityEngine()

    def _parse_currency(self, value):
        """Convert currency string like Rs10,00,000 to numeric value"""
        if isinstance(value, (int, float)):
            return value
        
        if not value or not isinstance(value, str):
            return 0
        
        # Remove Rs symbol and commas
        clean_value = value.replace('Rs', '').replace('₹', '').replace(',', '')
        
        try:
            return float(clean_value)
        except (ValueError, TypeError):
            return 0

    def _parse_percentage(self, value):
        """Convert percentage string like 9.2% to numeric value"""
        if isinstance(value, (int, float)):
            return value
        
        if not value or not isinstance(value, str):
            return 0
        
        # Remove % symbol
        clean_value = value.replace('%', '')
        
        try:
            return float(clean_value)
        except (ValueError, TypeError):
            return 0

    def _parse_years(self, value):
        """Convert string like '5 years' to numeric value"""
        if isinstance(value, (int, float)):
            return value
        
        if not value or not isinstance(value, str):
            return 0
        
        # Extract first numeric part
        parts = value.split()
        try:
            return int(parts[0])
        except (ValueError, IndexError):
            return 0

    def _parse_int(self, value, default=0):
        """Parse any value to int with proper error handling"""
        if isinstance(value, int):
            return value
            
        if isinstance(value, float):
            return int(value)
            
        if not value:
            return default
            
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default

    def _format_applicant_data_for_eligibility(self, applicant_data):
        """
        Transform the applicant data format to match what the eligibility engine expects
        """
        # Extract financial data
        credit_score = self._parse_int(applicant_data.get('financial', {}).get('credit_score', 0))
        monthly_income = self._parse_currency(applicant_data.get('financial', {}).get('monthly_income', 0))
        monthly_expenses = self._parse_currency(applicant_data.get('financial', {}).get('monthly_expenses', 0))
        
        # Extract employment data
        work_experience = self._parse_years(applicant_data.get('employment', {}).get('work_experience', 0))
        
        # Extract loan request data
        loan_amount = self._parse_currency(applicant_data.get('loan_request', {}).get('loan_amount', 0))
        loan_term = self._parse_years(applicant_data.get('loan_request', {}).get('loan_term', 0))
        interest_rate = self._parse_percentage(applicant_data.get('loan_request', {}).get('interest_rate', 0))
        property_value = self._parse_currency(applicant_data.get('loan_request', {}).get('property_value', 0))
        
        return {
            'financial': {
                'credit_score': credit_score,
                'monthly_expenses': monthly_expenses
            },
            'employment': {
                'net_monthly_salary': monthly_income,
                'work_experience': work_experience
            },
            'loan_request': {
                'loan_amount': loan_amount,
                'loan_term': loan_term,
                'interest_rate': interest_rate,
                'property_value': property_value
            }
        }

    def analyze_key_eligibility_factors(self, applicant_data, eligibility_results):
        """Analyze the 5 key eligibility factors"""
        # Extract formatted data
        formatted_data = self._format_applicant_data_for_eligibility(applicant_data)
        
        # Get criteria from eligibility engine
        criteria = self.eligibility_engine.criteria
        
        # Extract relevant values - ensure all are proper numeric types
        credit_score = self._parse_int(formatted_data['financial']['credit_score'])
        monthly_income = float(formatted_data['employment']['net_monthly_salary'])
        monthly_expenses = float(formatted_data['financial']['monthly_expenses'])
        work_experience = int(formatted_data['employment']['work_experience'])
        loan_amount = float(formatted_data['loan_request']['loan_amount'])
        property_value = float(formatted_data['loan_request']['property_value'])
        
        # Calculate ratios (with safety checks for zero division)
        dti_ratio = monthly_expenses / monthly_income if monthly_income > 0 else 1.0
        ltv_ratio = loan_amount / property_value if property_value > 0 else 1.0
        
        # Format factors
        key_factors = [
            {
                "factor_name": "Credit Score",
                "value": credit_score,
                "threshold": criteria['minimum_credit_score'],
                "status": "PASS" if credit_score >= criteria['minimum_credit_score'] else "FAIL",
                "description": "Credit score is a measure of creditworthiness based on credit history."
            },
            {
                "factor_name": "Income Level",
                "value": f"₹{monthly_income:,.2f}",
                "threshold": f"₹{criteria['minimum_income']:,.2f}",
                "status": "PASS" if monthly_income >= criteria['minimum_income'] else "FAIL",
                "description": "Monthly income should be sufficient to cover loan payments."
            },
            {
                "factor_name": "Debt-to-Income Ratio",
                "value": f"{dti_ratio:.2f}",
                "threshold": f"{criteria['maximum_dti_ratio']}",
                "status": "PASS" if dti_ratio <= criteria['maximum_dti_ratio'] else "FAIL",
                "description": "The ratio of monthly expenses to income should be below the threshold."
            },
            {
                "factor_name": "Employment Stability",
                "value": f"{work_experience} years",
                "threshold": f"{criteria['minimum_employment_years']} years",
                "status": "PASS" if work_experience >= criteria['minimum_employment_years'] else "FAIL",
                "description": "Stable employment history is required for loan approval."
            },
            {
                "factor_name": "Loan-to-Value Ratio",
                "value": f"{ltv_ratio:.2f}",
                "threshold": f"{criteria['loan_to_value_ratio']}",
                "status": "PASS" if ltv_ratio <= criteria['loan_to_value_ratio'] else "FAIL",
                "description": "The ratio of loan amount to asset value should be below the threshold."
            }
        ]
        
        return key_factors

    def generate_report(self, applicant_data_file):
        """
        Generate a comprehensive loan application report
        """
        # Load applicant data
        try:
            with open(applicant_data_file, 'r') as f:
                applicant_data = json.load(f)
        except Exception as e:
            print(f"Error loading applicant data: {e}")
            return None
        
        # Format data for eligibility check
        eligibility_formatted_data = self._format_applicant_data_for_eligibility(applicant_data)
        
        # Check eligibility
        try:
            eligibility_results = self.eligibility_engine.check_eligibility(eligibility_formatted_data)
        except Exception as e:
            print(f"Error checking eligibility: {e}")
            # Provide default eligibility results if check fails
            eligibility_results = {
                "status": "NEEDS_MORE_INFO",
                "factors": ["Error processing eligibility"],
                "recommendations": ["Please review your application data"]
            }
        
        # Analyze key eligibility factors
        try:
            key_factors = self.analyze_key_eligibility_factors(applicant_data, eligibility_results)
        except Exception as e:
            print(f"Error analyzing eligibility factors: {e}")
            import traceback
            traceback.print_exc()
            # Provide default factors if analysis fails
            key_factors = [{"factor_name": "Error", "description": str(e)}]
        
        # Extract personal information
        name = applicant_data.get('personal_information', {}).get('name', 'Unknown')
        dob = applicant_data.get('personal_information', {}).get('date_of_birth', 'Unknown')
        gender = applicant_data.get('personal_information', {}).get('gender', 'Unknown')
        
        # Extract loan details
        loan_amount = applicant_data.get('loan_request', {}).get('loan_amount', 'Unknown')
        loan_purpose = applicant_data.get('loan_request', {}).get('loan_purpose', 'Unknown')
        loan_term = applicant_data.get('loan_request', {}).get('loan_term', 'Unknown')
        interest_rate = applicant_data.get('loan_request', {}).get('interest_rate', 'Unknown')
        
        # Extract financial information
        monthly_income = applicant_data.get('financial', {}).get('monthly_income', 'Unknown')
        monthly_expenses = applicant_data.get('financial', {}).get('monthly_expenses', 'Unknown')
        credit_score = applicant_data.get('financial', {}).get('credit_score', 'Unknown')
        
        # Calculate EMI
        loan_amount_numeric = self._parse_currency(loan_amount)
        interest_rate_numeric = self._parse_percentage(interest_rate)
        loan_term_numeric = self._parse_years(loan_term)
        
        try:
            if loan_amount_numeric > 0 and interest_rate_numeric > 0 and loan_term_numeric > 0:
                emi = self.eligibility_engine.calculate_emi(
                    loan_amount_numeric, 
                    interest_rate_numeric, 
                    loan_term_numeric
                )
                emi_formatted = f"₹{emi:,.2f}"
            else:
                emi_formatted = "Cannot calculate"
        except Exception as e:
            print(f"Error calculating EMI: {e}")
            emi_formatted = "Error calculating"
        
        # Create the report
        report = {
            "report_date": "2025-03-17",
            "applicant": {
                "name": name,
                "date_of_birth": dob,
                "gender": gender
            },
            "loan_details": {
                "loan_amount": loan_amount,
                "loan_purpose": loan_purpose,
                "loan_term": loan_term,
                "interest_rate": interest_rate,
                "estimated_emi": emi_formatted
            },
            "financial_overview": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "credit_score": credit_score
            },
            "eligibility_assessment": {
                "overall_status": eligibility_results["status"],
                "key_factors": key_factors,
                "detailed_factors": eligibility_results["factors"],
                "recommendations": eligibility_results["recommendations"]
            },
            "conclusion": {
                "is_approved": eligibility_results["status"] == "APPROVED",
                "approval_type": eligibility_results["status"],
                "next_steps": "Please proceed with document verification" if eligibility_results["status"] in ["APPROVED", "CONDITIONALLY_APPROVED"] else "Please address the issues mentioned in the recommendations"
            }
        }
        
        return report

    def print_report(self, report):
        """Print a formatted report to the terminal"""
        if not report:
            print("No report available.")
            return
            
        print("\n" + "="*80)
        print(f"LOAN APPLICATION REPORT - {report['applicant']['name']}")
        print("="*80)
        
        print("\nAPPLICANT DETAILS:")
        print(f"  Name: {report['applicant']['name']}")
        print(f"  Date of Birth: {report['applicant']['date_of_birth']}")
        print(f"  Gender: {report['applicant']['gender']}")
        
        print("\nLOAN DETAILS:")
        print(f"  Amount: {report['loan_details']['loan_amount']}")
        print(f"  Purpose: {report['loan_details']['loan_purpose']}")
        print(f"  Term: {report['loan_details']['loan_term']}")
        print(f"  Interest Rate: {report['loan_details']['interest_rate']}")
        print(f"  Estimated EMI: {report['loan_details']['estimated_emi']}")
        
        print("\nFINANCIAL OVERVIEW:")
        print(f"  Monthly Income: {report['financial_overview']['monthly_income']}")
        print(f"  Monthly Expenses: {report['financial_overview']['monthly_expenses']}")
        print(f"  Credit Score: {report['financial_overview']['credit_score']}")
        
        print("\nELIGIBILITY STATUS:")
        status = report['eligibility_assessment']['overall_status']
        
        # Apply color based on status (works in compatible terminals)
        if status == "APPROVED":
            status_color = "\033[92m"  # Green
        elif status == "CONDITIONALLY_APPROVED":
            status_color = "\033[93m"  # Yellow
        elif status == "NEEDS_MORE_INFO":
            status_color = "\033[94m"  # Blue
        else:  # REJECTED
            status_color = "\033[91m"  # Red
            
        print(f"  Status: {status_color}{status}\033[0m")
        
        print("\nKEY ELIGIBILITY FACTORS:")
        for factor in report['eligibility_assessment']['key_factors']:
            factor_status = factor.get('status', 'UNKNOWN')
            if factor_status == "PASS":
                factor_color = "\033[92m"  # Green
            else:
                factor_color = "\033[91m"  # Red
                
            print(f"  {factor['factor_name']}: {factor_color}{factor_status}\033[0m")
            print(f"    Value: {factor.get('value', 'N/A')}")
            print(f"    Required: {factor.get('threshold', 'N/A')}")
            print(f"    Description: {factor.get('description', 'N/A')}")
            print("")
        
        if report['eligibility_assessment']['detailed_factors']:
            print("DETAILED FACTORS:")
            for factor in report['eligibility_assessment']['detailed_factors']:
                print(f"  - {factor}")
        
        if report['eligibility_assessment']['recommendations']:
            print("\nRECOMMENDATIONS:")
            for rec in report['eligibility_assessment']['recommendations']:
                print(f"  - {rec}")
        
        print("\nCONCLUSION:")
        conclusion_status = "APPROVED" if report['conclusion']['is_approved'] else report['conclusion']['approval_type']
        if report['conclusion']['is_approved']:
            conclusion_color = "\033[92m"  # Green
        else:
            conclusion_color = "\033[91m"  # Red
            
        print(f"  Status: {conclusion_color}{conclusion_status}\033[0m")
        print(f"  Next Steps: {report['conclusion']['next_steps']}")
        
        print("\n" + "="*80)
        print("\n")


if __name__ == "__main__":
    # Usage example
    try:
        report_generator = LoanReportGenerator()
        
        # Generate report from the file
        report = report_generator.generate_report("applicant_data_structured.json")
        
        # Print the report to terminal
        report_generator.print_report(report)
        
        # Save the report to a JSON file
        output_file = "loan_eligibility_report.json"
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
            print(f"Report saved to {output_file}")
            
    except Exception as e:
        print(f"Error generating report: {e}")
        # Print the full stack trace for debugging
        import traceback
        traceback.print_exc()