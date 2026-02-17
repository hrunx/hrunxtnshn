# hrunxtnshn Python Orchestrator

Custom Python backend using LangGraph for autonomous browsing agent orchestration.

## Features

- **LangGraph Agent**: Autonomous task planning and execution
- **FastAPI Backend**: High-performance async API server
- **Task Queue**: Concurrent task processing
- **Extension Bridge**: Communication with browser extension
- **Streaming Support**: Real-time task execution updates

## Architecture

The orchestrator uses LangGraph to create an agent workflow:

1. **Plan**: LLM analyzes the task and creates an action plan
2. **Execute**: Actions are executed sequentially using browser extension tools
3. **Synthesize**: Results are combined into a coherent response

### Agent Tools

- `load_page`: Load web pages invisibly
- `fetch_with_session`: Authenticated HTTP requests
- `extract_linkedin`: LinkedIn profile extraction
- `extract_instagram`: Instagram profile extraction
- `extract_maps`: Google Maps data extraction
- `wait`: Delay between actions

## Installation

### Prerequisites

- Python 3.11+
- pip or uv

### Setup

1. Navigate to the orchestrator directory:
   ```bash
   cd orchestrator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-your-api-key-here
   ```

## Usage

### Start the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### Configuration

Edit `.env` to configure:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4.1-mini)
- `OPENAI_BASE_URL`: API base URL (default: https://api.openai.com/v1)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)
- `API_KEY`: Optional API authentication key
- `EXTENSION_TIMEOUT`: Extension action timeout in seconds (default: 30)
- `MAX_CONCURRENT_TASKS`: Maximum concurrent tasks (default: 5)

### API Endpoints

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agent_ready": true
}
```

#### Create Task
```bash
POST /api/tasks
Content-Type: application/json

{
  "prompt": "Extract data from LinkedIn profile https://linkedin.com/in/example",
  "needsPlanning": true
}
```

Response:
```json
{
  "task_id": "uuid",
  "status": "completed",
  "result": {
    "result": { ... },
    "plan": [ ... ],
    "actions_executed": [ ... ]
  }
}
```

#### Get Task Status
```bash
GET /api/tasks/{task_id}
```

#### Stream Task Execution
```bash
POST /api/tasks/stream
Content-Type: application/json

{
  "prompt": "Your task description"
}
```

Returns Server-Sent Events (SSE) stream.

### With Authentication

If you set `API_KEY` in `.env`, include it in requests:

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Your task"}'
```

## Extension Integration

The orchestrator communicates with the browser extension through the extension bridge.

### Configure Extension

1. Open extension settings
2. Select "Custom Orchestrator" mode
3. Enter orchestrator endpoint: `http://localhost:8000`
4. (Optional) Enter API key if authentication is enabled
5. Save and test connection

### How It Works

1. Extension sends task to orchestrator via `/api/tasks`
2. Orchestrator creates agent execution plan
3. Agent executes actions by calling back to extension
4. Results are returned to extension

**Note**: The current implementation uses a simulated bridge. For production use, implement WebSocket or HTTP callback mechanism for bidirectional communication.

## Development

### Project Structure

```
orchestrator/
├── main.py                  # FastAPI application
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── api/
│   ├── models.py           # Pydantic models
│   └── routes.py           # API endpoints
├── agent/
│   ├── graph.py            # LangGraph agent
│   ├── nodes.py            # Agent nodes
│   ├── tools.py            # Agent tools
│   └── state.py            # Agent state
├── services/
│   ├── extension_bridge.py # Extension communication
│   └── task_queue.py       # Task queue management
└── utils/
    └── (utilities)
```

### Adding New Tools

1. Add tool method to `agent/tools.py`:
   ```python
   async def my_tool(self, param: str) -> Dict[str, Any]:
       """Tool description"""
       return await self.bridge.send_action({
           "action": "MY_ACTION",
           "param": param
       })
   ```

2. Add tool description to `get_tool_descriptions()`:
   ```python
   {
       "name": "my_tool",
       "description": "What the tool does",
       "parameters": {
           "param": "Parameter description"
       }
   }
   ```

3. Update agent nodes to handle the new action

### Testing

Test the orchestrator without the extension:

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Create task (will fail without extension connected)
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test task"}'
```

## Troubleshooting

### "Extension not connected" error

The orchestrator needs the browser extension to execute actions. Make sure:
1. The extension is installed and loaded
2. The extension is configured to use orchestrator mode
3. The extension endpoint matches the orchestrator URL

### Import errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### OpenAI API errors

Check your API key in `.env`:
- Key must start with `sk-`
- Key must be valid and have credits
- Base URL must be correct

### Port already in use

Change the port in `.env`:
```
PORT=8001
```

## Production Deployment

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t hrunxtnshn-orchestrator .
docker run -p 8000:8000 --env-file .env hrunxtnshn-orchestrator
```

### Using systemd

Create `/etc/systemd/system/hrunxtnshn.service`:
```ini
[Unit]
Description=hrunxtnshn Orchestrator
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/orchestrator
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable hrunxtnshn
sudo systemctl start hrunxtnshn
```

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please visit:
https://github.com/hrunx/hrunxtnshn/issues
