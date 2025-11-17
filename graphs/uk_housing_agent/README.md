# UK Housing Agent - Aegra Integration

This integration adds the UK Housing Agent as a graph within Aegra, allowing you to serve UK housing expertise through a self-hosted LangGraph backend.

## Features

🏠 **Housing-Focused AI Assistant** - Specialized in UK housing issues
🔧 **Multi-Agent Routing** - Automatically routes to specialist agents for:
  - Heating (boilers, radiators, temperature issues)
  - Damp (moisture, mold, condensation)
  - Repairs (plumbing, electrical, structural)
  - General (other housing matters)

🧠 **RAG Support** - Integrates with OpenSearch for knowledge base queries
📊 **Persistent Memory** - Thread-based conversation history
🎯 **Configurable** - Runtime configuration via Context

## Quick Start

### 1. Set Environment Variables

Edit `/home/aegra/.env` to add UK Housing Agent configuration:

```bash
# LLM Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE=https://api.openai.com/v1

# OpenSearch (optional, for RAG)
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=your-password

# Tracing (optional)
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=uk-housing-agent
```

### 2. Start Aegra

```bash
cd /home/aegra
docker-compose up aegra
```

### 3. Test the Graph

```bash
# Start server (already running from docker-compose)
# Test using Python SDK
python test_uk_housing_agent.py
```

## Usage Examples

### Using Python SDK

```python
import asyncio
from langgraph_sdk import get_client

async def main():
    client = get_client(url="http://localhost:8000")
    
    # Create assistant
    assistant = await client.assistants.create(
        graph_id="uk_housing",
        if_exists="do_nothing",
        config={
            "model": "gpt-4o-mini",
            "temperature": 0.7,
        }
    )
    
    # Create thread
    thread = await client.threads.create()
    
    # Stream responses
    stream = client.runs.stream(
        thread_id=thread["thread_id"],
        assistant_id=assistant["assistant_id"],
        input={
            "messages": [{
                "type": "human",
                "content": "My boiler is making a loud noise"
            }]
        },
        stream_mode=["values"],
    )
    
    async for chunk in stream:
        print(chunk)

asyncio.run(main())
```

### Using cURL

```bash
# Get assistant
curl -X POST http://localhost:8000/assistants \
  -H "Content-Type: application/json" \
  -d '{"graph_id": "uk_housing", "if_exists": "do_nothing"}'

# Create thread
curl -X POST http://localhost:8000/threads

# Stream run
curl -X POST http://localhost:8000/threads/{thread_id}/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "{assistant_id}",
    "input": {
      "messages": [{
        "type": "human",
        "content": "My radiator is cold"
      }]
    }
  }'
```

## Configuration Options

### Context Configuration

The UK Housing Agent accepts these runtime configuration options:

```python
config = {
    "model": "gpt-4o-mini",           # LLM to use
    "temperature": 0.7,                # Response randomness (0-1)
    "max_tokens": 1000,                # Max response length
    "openai_api_key": "sk-...",        # API key (auto-loaded from env)
    "openai_api_base": "https://...",  # API base URL
    "opensearch_host": "localhost",    # RAG database host
    "opensearch_port": 9200,           # RAG database port
    "opensearch_user": "admin",        # RAG database user
    "opensearch_password": "...",      # RAG database password
    "langsmith_api_key": "...",        # Tracing API key
    "langsmith_project": "uk-housing", # Tracing project
}
```

## Graph Flow

```
User Input
    ↓
[detect_intent] - Classify housing issue type
    ↓
[call_model] - LLM with tools
    ↓
    ├─ No tool calls? → END
    └─ Tool calls needed? → [tools]
                                ↓
                           [call_model] (loop until done)
```

## Available Tools

The UK Housing Agent has access to these tools:

1. **search_housing_knowledge** - Search knowledge base for housing advice
2. **get_boiler_info** - Get information about specific boiler brands
3. **get_repair_guidance** - Get guidance for repair issues

## Directory Structure

```
/home/aegra/graphs/uk_housing_agent/
├── __init__.py           # Package initialization
├── state.py              # State definitions (InputState, State)
├── context.py            # Configuration context
├── tools.py              # Tool definitions
└── graph.py              # Main graph logic
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| OPENAI_API_KEY | (required) | OpenAI API key |
| OPENAI_MODEL | gpt-4o-mini | Model to use |
| OPENAI_API_BASE | https://api.openai.com/v1 | API endpoint |
| OPENSEARCH_HOST | localhost | RAG database host |
| OPENSEARCH_PORT | 9200 | RAG database port |
| OPENSEARCH_USER | admin | RAG database user |
| OPENSEARCH_PASSWORD | (required for RAG) | RAG database password |
| LANGSMITH_API_KEY | (optional) | Tracing API key |
| LANGSMITH_PROJECT | uk-housing-agent | Tracing project name |

## Integration with Agent Chat UI

To use with LangChain's Agent Chat UI:

```bash
# In agent-chat-ui/.env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ASSISTANT_ID=uk_housing
```

Then access the UI at `http://localhost:3000` and select the UK Housing assistant.

## Troubleshooting

### Graph not found

If you see "graph not found" error:
1. Check `aegra.json` includes `"uk_housing": "./graphs/uk_housing_agent/graph.py:graph"`
2. Restart Aegra: `docker-compose down && docker-compose up aegra`

### Model errors

If the model isn't available:
1. Check `OPENAI_API_KEY` is set correctly
2. Check `OPENAI_API_BASE` is accessible
3. Verify `OPENAI_MODEL` exists

### OpenSearch not connecting

If RAG isn't working:
1. Check `OPENSEARCH_HOST` and `OPENSEARCH_PORT`
2. Verify credentials: `OPENSEARCH_USER`, `OPENSEARCH_PASSWORD`
3. Test connection: `curl -u user:pass http://opensearch-host:9200`

## Next Steps

- [ ] Integrate with actual OpenSearch knowledge base
- [ ] Add specialized tools for each agent type
- [ ] Implement human-in-the-loop approval workflows
- [ ] Add Langfuse tracing integration
- [ ] Deploy to production with proper authentication

## Support

For issues or questions:
1. Check Aegra logs: `docker-compose logs -f aegra`
2. Review [Aegra documentation](../docs)
3. Check [LangGraph documentation](https://langchain-ai.github.io/langgraph)
