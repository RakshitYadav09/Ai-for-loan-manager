from flask import Flask, request, jsonify, send_from_directory
from backend.conversation_manager import DynamicConversationManager
import os
import json

app = Flask(__name__, static_folder='frontend')

# Initialize the conversation manager
conversation_manager = DynamicConversationManager()

# Serve frontend files
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

def load_default_applicant_data(file_path='applicant_data_structured.json'):
    """Load default applicant data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found. Returning empty data.")
        return {
            "personal_information": {},
            "identification": {},
            "employment": {},
            "financial": {},
            "loan_request": {}
        }

# API Endpoint: Process user response
@app.route('/api/process-response', methods=['POST'])
def process_response():
    data = request.json
    user_response = data.get('user_response', '')
    applicant_data = data.get('applicant_data', {})

    # Load default applicant data if none is provided
    if not applicant_data:
        applicant_data = load_default_applicant_data()

    # Update conversation manager's applicant data
    conversation_manager.applicant_data = applicant_data

    # Process user response using Gemini AI integration
    response_data = conversation_manager.ai.handle_user_response(user_response, applicant_data)

    # Update applicant data with new information
    if response_data.get('data_updates'):
        for category, details in response_data['data_updates'].items():
            if category not in applicant_data:
                applicant_data[category] = {}
            for key, value in details.items():
                applicant_data[category][key] = value

    return jsonify({
        "applicant_data": applicant_data,
        "needs_clarification": response_data.get('needs_clarification', False),
        "clarification_question": response_data.get('clarification_question', '')
    })

# API Endpoint: Get next question from Gemini AI
@app.route('/api/next-question', methods=['POST'])
def next_question():
    data = request.json
    applicant_data = data.get('applicant_data', {})
    conversation_history = data.get('conversation_history', [])

    # Convert conversation history to string format expected by Gemini AI integration
    history_str = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in conversation_history])

    # Update conversation manager's applicant data
    conversation_manager.applicant_data = applicant_data

    # Get next question from Gemini AI integration
    next_question_text = conversation_manager.ai.get_next_question(applicant_data, history_str)

    return jsonify({"question": next_question_text})

# API Endpoint: Generate loan eligibility report
@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    data = request.json
    applicant_data = data.get('applicant_data', {})

    # Update conversation manager's applicant data
    conversation_manager.applicant_data = applicant_data

    # Generate JSON report using the conversation manager
    report_json = conversation_manager.generate_json_report()

    return jsonify(report_json)

if __name__ == '__main__':
    app.run(debug=True)
