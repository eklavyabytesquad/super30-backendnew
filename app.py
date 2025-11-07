from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from app import TextProcessor, process_json_file

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

if __name__ == '__main__':
    # Run the Flask app
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
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )