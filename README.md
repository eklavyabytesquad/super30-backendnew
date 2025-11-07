# Super30 Text Processing API 🚀

A powerful Flask-based REST API for text processing, cleaning, and summarization using advanced NLP techniques.

## 🌟 Features

- **Text Cleaning**: Remove emojis, special characters, and normalize text
- **Text Summarization**: Generate concise summaries using LSA (Latent Semantic Analysis)
- **CORS Support**: Cross-origin requests enabled for web applications
- **Multiple Input Methods**: Process single texts, JSON data, or upload files
- **RESTful API**: Clean, documented endpoints with JSON responses
- **Error Handling**: Comprehensive error handling with meaningful messages

## 📋 Requirements

- Python 3.7+
- Flask 2.3.0+
- Flask-CORS 4.0.0+
- Sumy 0.11.0+
- Other dependencies listed in `requirement.txt`

## 🚀 Quick Start

### 1. Installation

```powershell
# Clone the repository
git clone <your-repo-url>
cd super30-backend

# Install dependencies
pip install -r requirement.txt
```

### 2. Start the API Server

```powershell
# Option 1: Direct Python execution
python api.py

# Option 2: Use the PowerShell script (recommended)
.\run-api.ps1
```

The server will start on `http://localhost:5000` by default.

### 3. Test the API

Open `test-api.html` in your browser for an interactive test interface, or use the PowerShell script menu.

## 📚 API Endpoints

### Base URL: `http://localhost:5000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and available endpoints |
| GET | `/health` | Health check endpoint |
| POST | `/process-text` | Process a single text string |
| POST | `/process-json` | Process JSON data with descriptions |
| POST | `/upload-json` | Upload and process a JSON file |

## 🔧 API Usage Examples

### 1. Health Check
```bash
curl -X GET http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "text-processing-api"
}
```

### 2. Process Single Text
```bash
curl -X POST http://localhost:5000/process-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "🌟 Hello world! This is a test text with emojis and special characters.",
    "sentences_count": 2
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "original_text": "🌟 Hello world! This is a test text...",
    "cleaned_text": "Hello world! This is a test text...",
    "summary": "Hello world! This is a test text...",
    "character_count_original": 75,
    "character_count_cleaned": 65,
    "character_count_summary": 50
  }
}
```

### 3. Process JSON Data
```bash
curl -X POST http://localhost:5000/process-json \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "id": 1,
        "description": "Your text content here..."
      }
    ],
    "sentences_count": 3
  }'
```

### 4. Upload JSON File
```bash
curl -X POST http://localhost:5000/upload-json \
  -F "file=@input.json"
```

## 🎯 PowerShell Commands

### Quick Commands for Testing

```powershell
# Install dependencies
pip install -r requirement.txt

# Start the server
python api.py

# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET

# Test text processing
$testData = @{
    text = "Your test text here"
    sentences_count = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/process-text" -Method POST -Body $testData -ContentType "application/json"
```

### Using the PowerShell Script

```powershell
# Run the interactive script
.\run-api.ps1

# Available options:
# 1. Install dependencies
# 2. Start API server
# 3. Test API endpoints
# 4. Open test interface in browser
# 5. Show curl examples
# 6. Exit
```

## 🌐 Web Interface

Open `test-api.html` in your browser for a user-friendly interface to:
- Check server status
- Test all API endpoints
- View formatted responses
- See curl command examples

## 📝 Input/Output Format

### Text Processing Input
```json
{
  "text": "Your text content here",
  "sentences_count": 3
}
```

### JSON Data Input
```json
{
  "data": [
    {
      "id": 1,
      "description": "Text to be processed..."
    }
  ],
  "sentences_count": 3
}
```

### Sample Output
```json
{
  "success": true,
  "data": {
    "processed_items": [
      {
        "original_text": "...",
        "cleaned_text": "...",
        "summary": "...",
        "character_count_original": 150,
        "character_count_cleaned": 140,
        "character_count_summary": 75,
        "id": 1
      }
    ],
    "total_items": 1,
    "processing_info": {
      "language": "english",
      "summarization_method": "LSA (Latent Semantic Analysis)",
      "emoji_removal": true,
      "special_char_removal": true,
      "sentences_count": 3
    }
  }
}
```

## 🔒 CORS Support

CORS is enabled for all origins (`*`). For production use, configure specific allowed origins in `api.py`:

```python
CORS(app, origins=["http://localhost:3000", "https://yourdomain.com"])
```

## 🛠️ Configuration

Environment variables:
- `PORT`: Server port (default: 5000)
- `DEBUG`: Debug mode (default: False)

```powershell
# Set environment variables
$env:PORT = "8000"
$env:DEBUG = "True"
python api.py
```

## 📊 Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Missing or invalid input data
- **404 Not Found**: Endpoint not found
- **405 Method Not Allowed**: Invalid HTTP method
- **500 Internal Server Error**: Processing errors

Example error response:
```json
{
  "error": "Missing 'text' field in request body"
}
```

## Files Structure

```
super30-backendnew/
├── app.py              # Original CLI application
├── api.py              # Flask REST API server
├── test-api.html       # Web test interface
├── run-api.ps1         # PowerShell helper script
├── requirement.txt     # Python dependencies
├── render.yaml         # Deployment configuration
├── input.json          # Sample input file
├── sample_output.json  # Example output format
└── README.md          # This documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the provided tools
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the test interface at `test-api.html`
2. Use the PowerShell script for troubleshooting
3. Review the API documentation above
4. Open an issue on GitHub