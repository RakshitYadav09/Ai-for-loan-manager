import subprocess
import os
import sys
import time

def run_command(command, description=None):
    """Run a command and display its output in real-time"""
    print("\n" + "="*80)
    if description:
        print(f"🔶 {description}")
    print("="*80 + "\n")
    
    # Create and start the process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        shell=True
    )
    
    # Read and print output in real-time
    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
    
    # Wait for the process to complete
    process.wait()
    return process.returncode

def main():
    print("\n" + "="*80)
    print("🚀 LOAN BUDDY PROCESS MANAGER")
    print("="*80)
    print("\nThis script will run the complete LoanBuddy workflow:")
    print("1. Document Parser: Extract structured data from applicant documents")
    print("2. Voice Interaction: Have a conversation with the AI Loan Manager")
    print("3. Report Generation: Generate a comprehensive loan eligibility report")
    print("\nPress Enter to begin the process...")
    input()
    
    # Run Document Parser
    print("\n⏳ Starting Document Parser...\n")
    doc_parser_result = run_command(
        "python DocumentParser.py", 
        "DOCUMENT PARSER: Converting unstructured document text to structured data"
    )
    
    if doc_parser_result != 0:
        print("❌ Document Parser failed. Continuing with workflow, but results may be affected.")
        time.sleep(2)
    else:
        print("✅ Document Parser completed successfully!")
        time.sleep(1)
    
    # Run Voice Interaction
    print("\n⏳ Starting Voice Interaction...\n")
    voice_result = run_command(
        "python main.py", 
        "VOICE INTERACTION: Starting conversation with AI Loan Manager"
    )
    
    if voice_result != 0:
        print("❌ Voice Interaction module failed. Continuing with workflow.")
        time.sleep(2)
    else:
        print("✅ Voice Interaction completed successfully!")
        time.sleep(1)
    
    # Run Report Generation
    print("\n⏳ Starting Report Generation...\n")
    report_result = run_command(
        "python report_generation.py", 
        "REPORT GENERATION: Generating loan eligibility assessment"
    )
    
    if report_result != 0:
        print("❌ Report Generation failed.")
    else:
        print("✅ Report Generation completed successfully!")
    
    # Final message
    print("\n" + "="*80)
    print("🏁 LOAN BUDDY PROCESS COMPLETE")
    print("="*80)
    print("\nAll modules have been executed. Check the generated files for complete results.")
    print("Thanks for using LoanBuddy!")

if __name__ == "__main__":
    main()