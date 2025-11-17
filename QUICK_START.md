# Quick Start: Aegra + Agent Chat UI

## ⚡ 5-Minute Setup

### Option 1: Local Development (Recommended)

```bash
# Terminal 1: Start the backend
cd /home/aegra
uv install
docker compose up postgres -d
python3 scripts/migrate.py upgrade
uv run uvicorn src.agent_server.main:app --reload

# Terminal 2: Start the frontend
cd /home/agent-chat-ui
pnpm install
pnpm dev
```

**Then open:** http://localhost:3000

### Option 2: Docker (All-in-One)

```bash
cd /home
docker compose -f docker-compose.all.yml up -d
```

**Then open:** http://localhost:3000

---

## 🎯 Using Agent Chat UI

1. **Navigate to:** http://localhost:3000

2. **Configuration form appears:**
   - **API URL:** `http://localhost:8000`
   - **Assistant ID:** `agent` (or select another)
   - **API Key:** Leave blank (for local development)

3. **Click "Continue"**

4. **Start chatting!** 💬

---

## 📋 Available Agents

When prompted for "Assistant ID", choose from:

- `agent` - React Agent (default)
- `agent_hitl` - Human-in-the-Loop Agent
- `subgraph_agent` - Subgraph Agent
- `subgraph_hitl_agent` - Subgraph HITL Agent
- `uk_housing` - UK Housing Agent (if configured)

Each conversation is automatically saved in a thread.

---

## 🧪 Test the API

```bash
# List available models
curl http://localhost:8000/v1/models | jq

# Send a chat message
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agent",
    "messages": [{"role": "user", "content": "Hello!"}],
    "thread_id": "test-123"
  }' | jq
```

---

## 📚 Documentation

- **Full integration guide:** `/home/INTEGRATION_GUIDE.md`
- **Backend docs:** `/home/aegra/CLAUDE.md`
- **Frontend docs:** `/home/agent-chat-ui/README.md`
- **UK Housing Agent:** `/home/uk_housing_agent/README.md`

---

## 🛠️ Useful Commands

```bash
# Check if services are running
make test-openai-api

# View logs
make logs

# Clean up everything
make clean

# Reset database
make db-reset
```

---

## 🐛 Troubleshooting

**"Failed to connect to LangGraph server"**
- Ensure `http://localhost:8000` is running
- Check browser console for errors

**"Model not found"**
- Make sure you selected a valid agent ID from the list
- Check available models: `curl http://localhost:8000/v1/models`

**"Port already in use"**
- Try a different port: `uv run uvicorn src.agent_server.main:app --port 8001`

---

## 🚀 What's Included

✅ **OpenAI-compatible API**
- `/v1/models` - List available agents
- `/v1/chat/completions` - Send messages (streaming & non-streaming)

✅ **Agent Chat UI**
- Real-time streaming responses
- Multi-turn conversation memory
- Thread management
- Support for any LangGraph agent

✅ **Multi-Agent Support**
- Select any agent from `aegra.json`
- Each agent persists conversation history
- Easy to add new agents

✅ **Production Ready**
- Database persistence
- Authentication support
- Docker deployment
- Hot reload in development

---

## 📞 Next Steps

1. ✅ Explore available agents
2. ✅ Test different agents by changing Assistant ID
3. ✅ Customize agents for your use case
4. ✅ Deploy to production
5. ✅ Add your own agents

---

**Status:** ✅ Ready to use  
**Last Updated:** November 17, 2025
