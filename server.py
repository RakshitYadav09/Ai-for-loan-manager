from flask import Flask, jsonify, request
import os
import fitz 
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
    

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using PyMuPDF.
    """
    extracted_text = ""
    try:
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                print(page)
                extracted_text += page.get_text()
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")
    return extracted_text

@app.route('/api/process_pdf', methods=['POST'])
def process_pdf():
    """
    Endpoint to process text from an uploaded PDF file.
    """
    try:
        # Check if a file is included in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        # Check if the file has a valid name
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Check if the file is a PDF
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400

        # Save the uploaded file temporarily
        temp_file_path = os.path.join("temp", file.filename)
        print(file.filename)
        os.makedirs("temp", exist_ok=True)
        file.save(temp_file_path)

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(temp_file_path)

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Return the extracted text
        return jsonify({"extracted_text": extracted_text})

    except Exception as e:
        return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(debug=True, port=10000)