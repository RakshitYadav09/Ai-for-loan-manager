#!/usr/bin/env python
"""
Master orchestration script for the Loan Buddy application.
This script runs the entire loan application processing pipeline:
1. Parse documents using DocumentParser
2. Run the main application for voice interactions
3. Generate the final eligibility report
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "="*80)
    print(f"  {message}")
    print("="*80 + "\n")

def wait_for_keypress():
    """Wait for a keypress to continue"""
    if os.name == 'nt':  # For Windows
        print("\nPress any key to continue...")
        os.system('pause >nul')
    else:  # For Unix/Linux
        print("\nPress Enter to continue...")
        input()

def run_document_parser():
    """Run the document parser to process application documents"""
    print_header("STEP 1: DOCUMENT PARSING")
    print("Starting document parsing process...")
    
    try:
        from DocumentParser import DocumentParser
        
        print("Checking for input document...")
        if not os.path.exists('applicant_data.txt'):
            print("Warning: applicant_data.txt not found.")
            print("Creating a sample applicant_data.txt file for demonstration...")
            
            # Create a sample file if it doesn't exist
            with open('applicant_data.txt', 'w') as f:
                f.write("Sample applicant data for parsing demonstration.\n")
                f.write("Name: Amit Sharma\n")
                f.write("DOB: July 15, 1992\n")
                f.write("Address: 101, Rajendra Nagar, Mumbai\n")
        
        print("\nInitializing document parser...")
        parser = DocumentParser()
        
        print("Parsing applicant data...")
        parsed_data = parser.parse_document_from_file('applicant_data.txt')
        
        print("Saving parsed data to structured format...")
        parser.save_parsed_data(parsed_data, 'applicant_data_structured.json')
        
        print("\nDocument parsing completed successfully!")
        return True
        
    except ImportError as e:
        print(f"Error: {e}")
        print("DocumentParser module couldn't be imported. Please check installation.")
        return False
    except Exception as e:
        print(f"Error during document parsing: {e}")
        return False

def run_voice_interaction():
    """Run the main voice interaction module"""
    print_header("STEP 2: VOICE INTERACTION")
    print("Starting voice-based interaction module...")
    
    try:
        # Check if we should skip this step (for testing)
        if "--skip-voice" in sys.argv:
            print("Skipping voice interaction (--skip-voice flag detected)")
            return True
        
        # Run main.py as a subprocess
        print("Initializing voice assistant...")
        result = subprocess.run([sys.executable, 'main.py'], 
                               capture_output=True, 
                               text=True)
        
        if result.returncode != 0:
            print(f"Voice interaction completed with errors:\n{result.stderr}")
            return False
        else:
            print(result.stdout)
            print("\nVoice interaction completed successfully!")
            return True
            
    except Exception as e:
        print(f"Error running voice interaction: {e}")
        return False

def run_report_generation():
    """Run the report generation module"""
    print_header("STEP 3: REPORT GENERATION")
    print("Starting loan eligibility report generation...")
    
    try:
        from report_generation import LoanReportGenerator
        
        print("Checking for applicant data...")
        if not os.path.exists('applicant_data_structured.json'):
            print("Error: applicant_data_structured.json not found!")
            return False
        
        print("\nInitializing report generator...")
        report_generator = LoanReportGenerator()
        
        print("Generating eligibility report...")
        report = report_generator.generate_report("applicant_data_structured.json")
        
        if report:
            print("\nReport generated successfully!")
            
            # Print report to terminal
            report_generator.print_report(report)
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"loan_eligibility_report_{timestamp}.json"
            with open(output_file, "w") as f:
                import json
                json.dump(report, f, indent=2)
                print(f"\nReport saved to {output_file}")
                
            return True
        else:
            print("Error: Failed to generate report.")
            return False
            
    except ImportError as e:
        print(f"Error: {e}")
        print("Report generation module couldn't be imported.")
        return False
    except Exception as e:
        print(f"Error during report generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main orchestration function"""
    print_header("LOAN BUDDY - COMPLETE PROCESSING PIPELINE")
    print("Starting complete loan application processing...")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Track success of each step
    step_results = []
    
    # Step 1: Document Parsing
    parser_success = run_document_parser()
    step_results.append(("Document Parsing", parser_success))
    
    if parser_success:
        wait_for_keypress()
    else:
        print("\nError in document parsing step. Do you want to continue anyway? (y/n)")
        if input().lower() != 'y':
            return
    
    # Step 2: Voice Interaction
    voice_success = run_voice_interaction()
    step_results.append(("Voice Interaction", voice_success))
    
    if voice_success:
        wait_for_keypress()
    else:
        print("\nError in voice interaction step. Do you want to continue anyway? (y/n)")
        if input().lower() != 'y':
            return
    
    # Step 3: Report Generation
    report_success = run_report_generation()
    step_results.append(("Report Generation", report_success))
    
    # Final summary
    print_header("PROCESSING SUMMARY")
    for step, success in step_results:
        status = "\033[92mSuccess\033[0m" if success else "\033[91mFailed\033[0m"
        print(f"{step}: {status}")
    
    overall_success = all(success for _, success in step_results)
    if overall_success:
        print("\n\033[92mLoan application processing completed successfully!\033[0m")
    else:
        print("\n\033[91mLoan application processing completed with errors.\033[0m")
        print("Please check the logs for details.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)