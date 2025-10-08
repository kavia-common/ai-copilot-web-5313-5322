# AI Copilot Backend

FastAPI backend service for the AI Copilot web application. This service manages chat sessions and integrates with Google's Gemini API to provide AI-powered conversational assistance.

## Features

- **Session Management**: Create and maintain isolated chat sessions with unique UUIDs
- **Gemini API Integration**: Leverages Google's Gemini 1.5 Flash model for natural language understanding
- **RESTful API**: Clean REST endpoints for session and chat operations
- **CORS Enabled**: Configured to accept requests from the frontend at `http://localhost:3000`
- **OpenAPI Documentation**: Auto-generated API docs available at `/docs`

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key

## Installation

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**

   Create a `.env` file from the example template:
   
   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file and set your Gemini API key:

   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Obtain a Gemini API Key**

   To get your API key:
   
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key" or "Get API Key"
   - Copy the generated key and paste it into your `.env` file

   **Important**: Keep your API key secure and never commit it to version control.

## Running the Backend

Start the backend server on port 3001:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 3001
```

For development with auto-reload:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

The API will be available at:
- **Base URL**: `http://localhost:3001`
- **API Documentation**: `http://localhost:3001/docs`
- **OpenAPI Spec**: `http://localhost:3001/openapi.json`

## API Endpoints

### Health Check
- **GET** `/` - Verify the API is running

### Session Management
- **POST** `/api/sessions` - Create a new chat session
  - Returns: `{ "session_id": "uuid" }`

- **GET** `/api/sessions/{session_id}/history` - Retrieve message history for a session
  - Returns: `{ "session_id": "uuid", "messages": [...] }`

### Chat
- **POST** `/api/chat` - Send a message and receive AI response
  - Body: `{ "session_id": "uuid", "message": "your message" }`
  - Returns: `{ "session_id": "uuid", "reply": "AI response" }`

### Models
- **GET** `/api/models` - List available Gemini models for your API key
  - Returns: 
    ```json
    {
      "models": [
        {
          "name": "models/gemini-1.5-flash",
          "displayName": "Gemini 1.5 Flash",
          "inputTokenLimit": 1048576,
          "outputTokenLimit": 8192,
          "supportedGenerationMethods": ["generateContent"]
        }
      ],
      "count": 1
    }
    ```

## Configuration

### CORS Settings

The backend is configured to accept requests from:
- `http://localhost:3000` (default frontend)

To modify allowed origins, edit `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes | None |
| `GEMINI_MODEL` | Gemini model name to use (e.g., gemini-1.5-flash) | No | gemini-1.5-flash |

## Verification Instructions

Follow these steps to verify the complete session flow:

### 1. Start the Backend

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 3001
```

### 2. Test Health Check

```bash
curl http://localhost:3001/
```

Expected response: `{"message": "Healthy"}`
  
### 2b. List Available Gemini Models

Ensure your `.env` has `GEMINI_API_KEY` set, then:

```bash
curl http://localhost:3001/api/models
```

Expected response (fields may vary by account/region):

```json
{
  "models": [
    {
      "name": "models/gemini-1.5-flash",
      "displayName": "Gemini 1.5 Flash",
      "inputTokenLimit": 1048576,
      "outputTokenLimit": 8192,
      "supportedGenerationMethods": ["generateContent"]
    }
  ],
  "count": 1
}
```

If the key is missing, you will receive a 400 error:
```json
{"detail":"GEMINI_API_KEY is missing or not configured. Set it in your environment or .env file."}
```
If your key lacks permissions or an API error occurs, you'll receive a 500 error with a helpful message.

### 3. Create a Session

```bash
curl -X POST http://localhost:3001/api/sessions
```

Expected response: `{"session_id": "550e8400-e29b-41d4-a716-446655440000"}`

Copy the returned `session_id` for the next steps.

### 4. Send a Message

Replace `YOUR_SESSION_ID` with the session ID from step 3:

```bash
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID", "message": "Hello, can you help me?"}'
```

Expected response: `{"session_id": "YOUR_SESSION_ID", "reply": "AI response text..."}`

### 5. Retrieve History

```bash
curl http://localhost:3001/api/sessions/YOUR_SESSION_ID/history
```

Expected response:
```json
{
  "session_id": "YOUR_SESSION_ID",
  "messages": [
    {"role": "user", "content": "Hello, can you help me?"},
    {"role": "assistant", "content": "AI response text..."}
  ]
}
```

## Project Structure

```
ai_copilot_backend/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI application and routes
│   │   └── generate_openapi.py  # OpenAPI spec generator
│   ├── models/
│   │   └── schemas.py           # Pydantic models for validation
│   └── services/
│       ├── gemini_service.py    # Gemini API integration
│       └── session_manager.py   # Session and history management
├── interfaces/
│   └── openapi.json             # Generated OpenAPI specification
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

## Troubleshooting

### Error: "GEMINI_API_KEY environment variable is not set"

**Solution**: Ensure you have created a `.env` file with your API key. The backend loads environment variables from this file on startup.

### Error: "Service Unavailable" when sending chat messages

**Solution**: Verify your Gemini API key is valid. Try making a test request to the Gemini API directly or regenerate your key from Google AI Studio.

### CORS errors in browser console

**Solution**: Ensure the frontend is running on `http://localhost:3000`. If using a different port, update the `allow_origins` list in `src/api/main.py`.

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
flake8 src/
```

### Regenerating OpenAPI Specification

```bash
python -m src.api.generate_openapi
```

## License

This project is part of the AI Copilot application suite.
