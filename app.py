from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
import unicodedata
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import os
import sys

class TextProcessor:
    def __init__(self, language='english'):
        self.language = language
        self.stemmer = Stemmer(language)
        self.summarizer = LsaSummarizer(self.stemmer)
        self.summarizer.stop_words = get_stop_words(language)
    
    def remove_emojis_and_special_chars(self, text):
        """Remove emojis, special characters, and keep only alphanumeric characters, spaces, and basic punctuation"""
        # Remove emojis using Unicode categories
        text = ''.join(char for char in text if unicodedata.category(char) not in ['So', 'Sm', 'Sk', 'Sc'])
        
        # Keep only alphanumeric characters, spaces, and basic punctuation (.,!?;:)
        text = re.sub(r'[^\w\s.,!?;:\-\'"()]', '', text)
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def summarize_text(self, text, sentences_count=3):
        """Summarize the given text using LSA algorithm"""
        try:
            # Parse the text
            parser = PlaintextParser.from_string(text, Tokenizer(self.language))
            
            # Generate summary
            summary_sentences = self.summarizer(parser.document, sentences_count)
            
            # Convert sentences to string
            summary = ' '.join([str(sentence) for sentence in summary_sentences])
            
            return summary
        except Exception as e:
            print(f"Error during summarization: {str(e)}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def process_text(self, text, sentences_count=3):
        """Main processing function that cleans text and summarizes it"""
        # Remove emojis and special characters
        cleaned_text = self.remove_emojis_and_special_chars(text)
        
        # Summarize the cleaned text
        summary = self.summarize_text(cleaned_text, sentences_count)
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "summary": summary,
            "character_count_original": len(text),
            "character_count_cleaned": len(cleaned_text),
            "character_count_summary": len(summary)
        }

def process_json_file(input_file, output_file):
    """Process JSON file and save results"""
    try:
        # Initialize text processor
        processor = TextProcessor()
        
        # Read input JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # Process each item in the input
        results = []
        
        if isinstance(input_data, list):
            for item in input_data:
                if 'description' in item:
                    processed_item = processor.process_text(item['description'])
                    processed_item['id'] = item.get('id', len(results) + 1)
                    results.append(processed_item)
        elif isinstance(input_data, dict) and 'description' in input_data:
            processed_item = processor.process_text(input_data['description'])
            processed_item['id'] = input_data.get('id', 1)
            results.append(processed_item)
        else:
            raise ValueError("Input JSON must contain 'description' field")
        
        # Prepare output data
        output_data = {
            "processed_items": results,
            "total_items": len(results),
            "processing_info": {
                "language": "english",
                "summarization_method": "LSA (Latent Semantic Analysis)",
                "emoji_removal": True,
                "special_char_removal": True
            }
        }
        
        # Write output JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Processing completed successfully!")
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        print(f"Processed {len(results)} items")
        
        return output_data
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{input_file}'.")
        return None
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return None

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["*"])

# Initialize text processor
text_processor = TextProcessor()

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Super30 Text Processing API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API information",
            "POST /process-text": "Process single text (body: {'text': 'your text', 'sentences_count': 3})",
            "POST /process-json": "Process JSON with descriptions (body: {'data': [...]})",
            "POST /upload-json": "Upload and process JSON file",
            "GET /health": "Health check"
        },
        "status": "active"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "text-processing-api"
    })

@app.route('/process-text', methods=['POST'])
def process_single_text():
    """Process a single text string"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "error": "Missing 'text' field in request body"
            }), 400
        
        text = data['text']
        sentences_count = data.get('sentences_count', 3)
        
        if not isinstance(sentences_count, int) or sentences_count < 1:
            sentences_count = 3
        
        # Process the text
        result = text_processor.process_text(text, sentences_count)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Processing failed: {str(e)}"
        }), 500

@app.route('/process-json', methods=['POST'])
def process_json_data():
    """Process JSON data with descriptions"""
    try:
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({
                "error": "Missing 'data' field in request body"
            }), 400
        
        input_data = data['data']
        sentences_count = data.get('sentences_count', 3)
        
        # Process each item in the input
        results = []
        
        if isinstance(input_data, list):
            for i, item in enumerate(input_data):
                if 'description' in item:
                    processed_item = text_processor.process_text(item['description'], sentences_count)
                    processed_item['id'] = item.get('id', i + 1)
                    processed_item['original_id'] = item.get('id')
                    results.append(processed_item)
        elif isinstance(input_data, dict) and 'description' in input_data:
            processed_item = text_processor.process_text(input_data['description'], sentences_count)
            processed_item['id'] = input_data.get('id', 1)
            results.append(processed_item)
        else:
            return jsonify({
                "error": "Input data must contain 'description' field"
            }), 400
        
        # Prepare response
        response_data = {
            "success": True,
            "data": {
                "processed_items": results,
                "total_items": len(results),
                "processing_info": {
                    "language": "english",
                    "summarization_method": "LSA (Latent Semantic Analysis)",
                    "emoji_removal": True,
                    "special_char_removal": True,
                    "sentences_count": sentences_count
                }
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "error": f"Processing failed: {str(e)}"
        }), 500

@app.route('/upload-json', methods=['POST'])
def upload_json_file():
    """Upload and process a JSON file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "error": "No file uploaded"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "error": "No file selected"
            }), 400
        
        if file and file.filename.endswith('.json'):
            # Save uploaded file temporarily
            temp_filename = f"temp_{file.filename}"
            file.save(temp_filename)
            
            try:
                # Process the file
                result = process_json_file(temp_filename, "temp_output.json")
                
                if result:
                    # Read the processed result
                    with open("temp_output.json", 'r', encoding='utf-8') as f:
                        output_data = json.load(f)
                    
                    # Clean up temporary files
                    os.remove(temp_filename)
                    os.remove("temp_output.json")
                    
                    return jsonify({
                        "success": True,
                        "data": output_data
                    })
                else:
                    # Clean up temporary file
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                    
                    return jsonify({
                        "error": "Failed to process the uploaded file"
                    }), 500
                    
            except Exception as e:
                # Clean up temporary file
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                raise e
        else:
            return jsonify({
                "error": "Please upload a valid JSON file"
            }), 400
            
    except Exception as e:
        return jsonify({
            "error": f"Upload processing failed: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "Please check the API documentation at the root endpoint '/'"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "error": "Method not allowed",
        "message": "Please check the allowed methods for this endpoint"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "Something went wrong on the server"
    }), 500

def main():
    """Main function to run the CLI application (legacy support)"""
    input_file = "input.json"
    output_file = "output.json"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' not found. Please create it first.")
        return
    
    # Process the file
    result = process_json_file(input_file, output_file)
    
    if result:
        print("\n=== Processing Summary ===")
        print(f"Total items processed: {result['total_items']}")
        print(f"Output saved to: {output_file}")
    else:
        print("Processing failed. Please check your input file and try again.")

if __name__ == "__main__":
    # Check if running as CLI or web server
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Run as CLI application
        main()
    else:
        # Run as Flask web server
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        print("="*50)
        print("🚀 Super30 Text Processing API")
        print("="*50)
        print(f"📡 Server running on: http://localhost:{port}")
        print(f"🔧 Debug mode: {debug}")
        print("📚 Available endpoints:")
        print("   GET  /              - API information")
        print("   GET  /health        - Health check")
        print("   POST /process-text  - Process single text")
        print("   POST /process-json  - Process JSON data")
        print("   POST /upload-json   - Upload JSON file")
        print("="*50)
        print("💡 To run as CLI: python app.py cli")
        print("="*50)
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug
        )