from flask import Flask, jsonify, request
import os
from report_generation import LoanReportGenerator

app = Flask(__name__)

# Initialize the report generator
report_generator = LoanReportGenerator()

@app.route('/api/report', methods=['GET'])
def get_report():
    """Return the pre-generated report as JSON"""
    try:
        # Check if the report file exists
        report_file = "loan_eligibility_report.json"
        if os.path.exists(report_file):
            with open(report_file, 'r') as f:
                import json
                return jsonify(json.load(f))
        else:
            return jsonify({"error": "Report not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error reading report: {str(e)}"}), 500

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """Generate a new report from applicant data file path provided in request"""
    try:
        data = request.json
        applicant_data_file = data.get('applicant_data_file')
        
        if not applicant_data_file or not os.path.exists(applicant_data_file):
            return jsonify({"error": "Invalid or missing applicant data file"}), 400
            
        # Generate the report
        report = report_generator.generate_report(applicant_data_file)
        
        if report:
            # Save the report
            output_file = "loan_eligibility_report.json"
            with open(output_file, "w") as f:
                import json
                json.dump(report, f, indent=2)
            
            return jsonify(report)
        else:
            return jsonify({"error": "Failed to generate report"}), 500
    except Exception as e:
        return jsonify({"error": f"Error generating report: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)