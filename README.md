# Bible Verse of the Day Agent

A FastAPI-based agent that provides daily Bible verses with AI-powered reflections, compatible with the Telex A2A protocol.

## Features

- **Dynamic Verse Retrieval**: Accepts user prompts and uses AI to extract topics for relevant Bible verses
- **Daily Verse Clock System**: Automatically posts daily verses at a configurable UTC time
- **AI Integration**: Uses gemini-2.5-flash for topic extraction and verse reflections
- **A2A Protocol Compliance**: Supports JSON-RPC 2.0 with `message/send` and `execute` methods
- **Configurable**: Translation and API settings via environment variables
- **Error Handling**: Comprehensive error handling for API failures and invalid requests

## Installation

1. Clone the repository
2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   TELEX_WEBHOOK_URL=https://ping.telex.im/v1/webhooks/your-webhook-id
   DAILY_POST_TIME=08:00
   DEFAULT_TRANSLATION=NIV
   ```

## Configuration

The following environment variables can be set:

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `TELEX_BASE_URL`: Telex API base URL (default: https://api.telex.im)
- `TELEX_WEBHOOK_URL`: Webhook URL for posting daily verses to Telex (required for daily posts)
- `DAILY_POST_TIME`: UTC time for daily posts (default: "08:00")
- `DEFAULT_TRANSLATION`: Bible translation (default: "NIV")

## Usage

### Running the Application

```bash
python main.py
```

The server will start on `http://localhost:8000`.

### API Endpoints

#### POST /a2a

Main A2A protocol endpoint supporting JSON-RPC 2.0 requests.

**Example Request (message/send):**

```json
{
  "jsonrpc": "2.0",
  "id": "123",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{ "kind": "text", "text": "Get a verse on love" }]
    }
  }
}
```

**Example Request (execute):**

```json
{
  "jsonrpc": "2.0",
  "id": "456",
  "method": "execute",
  "params": {
    "messages": [
      {
        "role": "user",
        "parts": [{ "kind": "text", "text": "Get a verse on faith" }]
      }
    ],
    "contextId": "ctx-123",
    "taskId": "task-456"
  }
}
```

**Example Response:**

```json
{
  "jsonrpc": "2.0",
  "id": "123",
  "result": {
    "id": "task-123",
    "contextId": null,
    "status": {
      "state": "completed",
      "message": "Verse retrieved successfully"
    },
    "artifacts": [
      {
        "name": "bible_verse",
        "parts": [
          {
            "kind": "text",
            "text": "Topic: love\nVerse: 1 John 4:8 (NIV)\nText: Whoever does not love does not know God, because God is love.\nReflection: This verse reminds us that love is the essence of God's nature."
          }
        ]
      }
    ],
    "history": [
      {
        "role": "user",
        "parts": [{ "kind": "text", "text": "Get a verse on love" }]
      },
      {
        "role": "assistant",
        "parts": [{ "kind": "text", "text": "Verse retrieved successfully" }]
      }
    ]
  }
}
```

## Testing

Run the test suite:

```bash
pytest
```

Run specific test files:

```bash
pytest test_models.py
pytest test_ai_service.py
pytest test_bible_api.py
pytest test_main.py
```

## Architecture

- **main.py**: FastAPI application with A2A endpoints and scheduler
- **models.py**: Pydantic models for A2A protocol and responses
- **ai_service.py**: Google Gemini integration for topic extraction and reflections
- **bible_api.py**: Bible API client using labs.bible.org
- **scheduler.py**: APScheduler for daily verse posting
- **config.py**: Configuration management

## Dependencies

- FastAPI: Web framework
- APScheduler: Background task scheduling
- Google Generative AI (Gemini): AI integration
- Requests: HTTP client for Bible API
- Pydantic: Data validation
- Python-dotenv: Environment variable management
- Pytest: Testing framework
- HTTPX: Async HTTP client for testing

## Daily Verse Posting

The agent automatically posts daily verses to Telex channels using webhooks. To set this up:

1. **Get your Telex Webhook URL**: In your Telex integration settings, find the webhook URL (usually `https://ping.telex.im/v1/webhooks/your-webhook-id`)

2. **Configure Environment Variables**:

   ```env
   TELEX_WEBHOOK_URL=https://ping.telex.im/v1/webhooks/your-webhook-id
   DAILY_POST_TIME=08:00  # UTC time
   ```

3. **Webhook Message Format**:
   ```json
   {
     "event_name": "daily_verse",
     "message": "📖 **Daily Bible Verse**\n\n**Genesis 1:1**\nIn the beginning God created the heavens and the earth.\n\n💭 *This verse speaks to the importance of faith in our spiritual journey.*",
     "status": "success",
     "username": "Bible Verse Bot"
   }
   ```

## Future Improvements

- **Redis Integration**: Add Redis for caching verses and storing daily verse data to optimize performance and reduce API calls
- **Multi-user Support**: Extend the agent to handle multiple users and persistent contexts
- **Advanced Scheduling**: Implement more flexible scheduling options for daily verses

## License

This project is licensed under the MIT License.
