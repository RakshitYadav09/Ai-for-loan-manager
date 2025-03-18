import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

class DocumentParser:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        genai.configure(api_key=api_key)
        
        # Use Gemini Pro for parsing
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            print(f"Error initializing Gemini model: {e}")
            print("Falling back to Gemini 1.5 Pro")
            self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def parse_document(self, document_text):
        """Parse unstructured document text into structured JSON format"""
        prompt = f"""
        You are a document parsing assistant. Convert the following document text into a structured JSON object.
        The text appears to be from multiple identification documents like ID cards,financial credentials, etc.
        
        Extract all relevant information and organize it into appropriate categories like:
        - personal_information (name, date_of_birth, gender, etc.)
        - identification (IDs like PAN card, Aadhar number, etc.)
        - contact (phone, email, addresses)
        - family (parent names, etc.)
        
        Document Text:
        ```
        {document_text}
        ```
        
        Return ONLY the JSON object with no additional text or explanation. 
        Ensure it's properly formatted and valid JSON.
        """
        
        response = self.model.generate_content(prompt)
        
        # Clean and parse the response
        try:
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "", 1)
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            parsed_data = json.loads(response_text)
            return parsed_data
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Raw response: {response.text}")
            return {"error": "Failed to parse document"}
    
    def parse_document_from_file(self, file_path):
        """Parse a document from a file and return structured data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                document_text = file.read()
            return self.parse_document(document_text)
        except Exception as e:
            print(f"Error reading file: {e}")
            return {"error": f"Failed to read file: {e}"}
    
    def save_parsed_data(self, parsed_data, output_file='applicant_data.txt'):
        """Save parsed data to a JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(parsed_data, file, indent=2, ensure_ascii=False)
            print(f"Parsed data saved to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving parsed data: {e}")
            return False

# Example usage
if __name__ == "__main__":
    parser = DocumentParser()
    
    # Parse from applicant_data.json (which currently contains raw OCR text)
    parsed_data = parser.parse_document_from_file('applicant_data.txt')
    
    # Save to structured JSON
    if parsed_data:
        parser.save_parsed_data(parsed_data, 'applicant_data_structured.json')