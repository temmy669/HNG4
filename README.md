# Bible Verse of the Day Agent

A FastAPI-based agent that provides daily Bible verses with AI-powered reflections, compatible with the Telex A2A protocol.

## Features

- **Dynamic Verse Retrieval**: Accepts user prompts and uses AI to extract topics for relevant Bible verses
- **Daily Verse Clock System**: Automatically posts daily verses at a configurable UTC time
- **AI Integration**: Uses gemini-2.5-flash for topic extraction and verse reflections
- **A2A Protocol Compliance**: Supports JSON-RPC 2.0 with `message/send` and `execute` methods
- **Webhook Integration**: Supports both blocking and non-blocking webhook notifications for real-time responses
- **Dynamic Webhook Configuration**: Automatically learns and stores webhook URLs and authentication from incoming Telex requests
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
   BIBLE_API_KEY=your_api_bible_key_here --> If applicable
   TELEX_WEBHOOK_HOOK_ID= your_hook_id   TELEX_BEARER_TOKEN=your_bearer_token_here
   DAILY_POST_TIME=08:00
   DEFAULT_TRANSLATION=NIV
   ```

## Configuration

The following environment variables can be set:

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `TELEX_BASE_URL`: Telex API base URL (default: https://api.telex.im)
- `TELEX_WEBHOOK_URL`: Webhook URL for posting daily verses to a Telex chanel (required for daily posts)
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

- **main.py**: FastAPI application with A2A endpoints, webhook configuration storage, and scheduler
- **models.py**: Pydantic models for A2A protocol and responses
- **ai_service.py**: Google Gemini integration for topic extraction and reflections
- **bible_api.py**: Bible API client using labs.bible.org
- **scheduler.py**: APScheduler for daily verse posting with dynamic webhook support
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

The agent automatically posts daily verses to Telex channels using A2A webhooks. There are two ways to configure webhook delivery:

### Method 1: Environment Variables (Static Configuration)

Set these in your `.env` file:

```env
TELEX_WEBHOOK_HOOK_ID=your_hook_id
TELEX_BEARER_TOKEN=your_bearer_token
DAILY_POST_TIME=08:00  # UTC time
```

### Method 2: Dynamic Configuration (Recommended)

The agent automatically learns webhook configuration from incoming Telex requests. When a user sends a request with `pushNotificationConfig`, the agent stores the URL and authentication details for future daily verse posting.

**How it works:**

1. User sends a request to `/a2a` with `pushNotificationConfig` containing URL and token
2. Agent extracts and stores this configuration
3. Daily scheduler uses the stored configuration to post verses
4. No manual webhook setup required - the agent learns from interactions

### A2A Webhook Message Format

Daily verses are sent in this JSON-RPC format:

```json
{
  "jsonrpc": "2.0",
  "id": "75d53d9705054a60b1cb2d2d1887c242",
  "method": "message/send",
  "params": {
    "message": {
      "kind": "message",
      "role": "agent",
      "parts": [
        {
          "kind": "text",
          "text": "📖 **Daily Bible Verse**\n\n**Genesis 1:1**\nIn the beginning God created the heavens and the earth.\n\n💭 *This verse speaks to the importance of faith in our spiritual journey.*",
          "metadata": null
        }
      ],
      "messageId": "db84ba2b62a0422e968d56591b9bb01a",
      "contextId": null,
      "taskId": null
    },
    "metadata": null
  }
}
```

## Future Improvements

- **Redis Integration**: Add Redis for caching verses and storing daily verse data to optimize performance and reduce API calls
- **Multi-user Support**: Extend the agent to handle multiple users and persistent contexts
- **Advanced Scheduling**: Implement more flexible scheduling options for daily verses

## License

This project is licensed under the MIT License.
