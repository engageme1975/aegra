# Aegra + Agent Chat UI: Complete Integration

> **Production-Ready AI Agent Chat Application**  
> Connect the Agent Chat UI frontend with Aegra backend for seamless multi-agent conversations.

---

## 📦 What You Have

### Backend: Aegra
- **Framework:** FastAPI + LangGraph
- **Location:** `/home/aegra`
- **Status:** ✅ Production ready
- **Features:**
  - OpenAI-compatible API endpoints
  - Multi-graph support
  - PostgreSQL state persistence
  - Authentication support

### Frontend: Agent Chat UI
- **Framework:** Next.js + React
- **Location:** `/home/agent-chat-ui`
- **Status:** ✅ Production ready
- **Features:**
  - Real-time streaming chat
  - Multi-turn memory
  - Thread management
  - Dark mode support

### Agents: LangGraph
- **Location:** `/home/aegra/graphs/`
- **Available:**
  - React Agent (default)
  - Human-in-the-Loop agents
  - Subgraph agents
  - UK Housing Agent

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
```bash
# Check Python
python3 --version  # Should be 3.11+

# Check Node
node --version     # Should be 18+

# Check Docker
docker --version
```

### Start Services

**Option A: Local Development (Recommended)**

```bash
# Terminal 1: Backend
cd /home/aegra
uv install
docker compose up postgres -d
python3 scripts/migrate.py upgrade
uv run uvicorn src.agent_server.main:app --reload

# Terminal 2: Frontend
cd /home/agent-chat-ui
pnpm install
pnpm dev
```

**Option B: Docker All-in-One**

```bash
cd /home
docker compose -f docker-compose.all.yml up -d
```

### Access

Open browser: **http://localhost:3000**

Configure:
- API URL: `http://localhost:8000`
- Assistant ID: `agent`
- API Key: (leave blank)

Click "Continue" → Start chatting!

---

## 🎯 Key Features

### 1. OpenAI-Compatible API

All agents are exposed as OpenAI-compatible chat completion endpoints:

```bash
# List available models/agents
curl http://localhost:8000/v1/models

# Chat (non-streaming)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agent",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Chat (streaming)
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agent",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

### 2. Multi-Agent Selection

Change agents in the chat UI:
```
Available agents:
├─ agent (default)
├─ agent_hitl
├─ subgraph_agent
├─ subgraph_hitl_agent
└─ uk_housing (if configured)
```

### 3. Thread Management

Each conversation gets a thread ID for persistent memory:

```javascript
// Automatic: UI generates thread-xxx
// Custom: ?threadId=my-thread-id
// Shared: Use same thread ID across devices
```

### 4. Streaming Responses

Messages stream in real-time as they're generated:

```javascript
// Handled automatically by Agent Chat UI
// See text appear character-by-character
```

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [`QUICK_START.md`](/home/QUICK_START.md) | 5-minute setup guide |
| [`INTEGRATION_GUIDE.md`](/home/INTEGRATION_GUIDE.md) | Complete integration documentation |
| [`/home/aegra/CLAUDE.md`](/home/aegra/CLAUDE.md) | Aegra backend architecture |
| [`/home/agent-chat-ui/README.md`](/home/agent-chat-ui/README.md) | Frontend setup & features |
| [`/home/uk_housing_agent/README.md`](/home/uk_housing_agent/README.md) | UK Housing Agent docs |

---

## 🔧 Management Commands

```bash
# View all commands
make help

# Development
make setup              # Install all dependencies
make start              # Start services locally
make start-docker       # Start with Docker
make stop               # Stop all services

# Testing
make test               # Run integration tests
make test-openai-api    # Test OpenAI API endpoints

# Database
make db-up              # Start PostgreSQL
make db-migrate         # Run migrations
make db-reset           # Reset database (destructive)

# Logs
make logs               # Show service logs
make logs-docker        # Show Docker logs
```

---

## 📁 Directory Structure

```
/home/
├── aegra/                          # Backend (FastAPI)
│   ├── src/agent_server/
│   │   ├── api/
│   │   │   ├── openai_compat.py   # ✨ OpenAI-compatible endpoints
│   │   │   ├── assistants.py      # Agent Protocol endpoints
│   │   │   ├── threads.py         # Thread management
│   │   │   └── runs.py            # Run management
│   │   └── main.py                # FastAPI app
│   ├── graphs/                     # LangGraph agents
│   ├── aegra.json                 # Graph registry
│   └── auth.py                    # Authentication config
│
├── agent-chat-ui/                 # Frontend (Next.js)
│   ├── src/
│   │   ├── app/                   # Next.js app
│   │   ├── components/            # React components
│   │   └── providers/Stream.tsx   # Stream provider
│   ├── .env                       # Environment config ✨
│   └── package.json
│
├── uk_housing_agent/              # Example: UK Housing Agent
│   ├── graph/workflow.py          # LangGraph definition
│   ├── server.py                  # OpenAI API server
│   └── README.md                  # Documentation
│
├── docker-compose.all.yml         # ✨ All-in-one Docker setup
├── Makefile                       # ✨ Management commands
├── QUICK_START.md                 # ✨ 5-minute guide
├── INTEGRATION_GUIDE.md           # ✨ Full documentation
└── test_integration.sh            # ✨ Integration tests

✨ = Created during this integration
```

---

## 🔌 Integration Points

### Backend → Frontend

```
http://localhost:3000
    ↓
.env: NEXT_PUBLIC_API_URL=http://localhost:8000
    ↓
http://localhost:8000/v1/models
http://localhost:8000/v1/chat/completions
http://localhost:8000/threads
http://localhost:8000/runs
```

### Frontend → Backend

```
Agent Chat UI
    ↓
OpenAI-compatible API
    ↓
LangGraph Agents
    ↓
PostgreSQL (state persistence)
```

---

## 🔐 Authentication

### Development (Default)

```bash
# No authentication required
AUTH_TYPE=noop
# Just set .env in agent-chat-ui and open http://localhost:3000
```

### Production (Custom)

```bash
# Enable authentication
AUTH_TYPE=custom

# Edit /home/aegra/auth.py to integrate with your auth service
# (Firebase, Auth0, JWT, etc.)

# Then agent-chat-ui will require API key:
# LangSmith API Key: lsv2_...
```

---

## 🧪 Testing

### Automated

```bash
# Run all tests
make test

# Or run manually
bash /home/test_integration.sh
```

### Manual

```bash
# 1. Backend health
curl http://localhost:8000/health
# Response: {"status": "ok"}

# 2. Models list
curl http://localhost:8000/v1/models | jq
# Response: {"object":"list","data":[{"id":"agent",...}]}

# 3. Chat test
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"agent","messages":[{"role":"user","content":"test"}]}'
# Response: {"id":"chatcmpl-...","choices":[...]}

# 4. Frontend
open http://localhost:3000
# Should see configuration form
```

---

## 🐛 Troubleshooting

### Backend Issues

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| Database error | `make db-up && make db-migrate` |
| Import errors | `cd aegra && uv install` |
| Graph not found | Check `/home/aegra/aegra.json` |

### Frontend Issues

| Issue | Solution |
|-------|----------|
| Port 3000 in use | `lsof -i :3000` then `kill -9 <PID>` |
| "Cannot reach API" | Verify `NEXT_PUBLIC_API_URL` in `.env` |
| No models loading | Check backend is running on port 8000 |
| Blank messages | Check browser console for errors |

### Network Issues

```bash
# Check backend is reachable
curl http://localhost:8000/health

# Check from Docker container
docker run --network host curlimages/curl http://localhost:8000/health

# Check DNS resolution
ping localhost
nslookup localhost
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Client Browser                      │
│              http://localhost:3000                   │
└────────────────────┬────────────────────────────────┘
                     │ HTTP + WebSocket
                     │ (OpenAI-compatible)
                     ↓
┌─────────────────────────────────────────────────────┐
│            Aegra Backend (FastAPI)                  │
│         http://localhost:8000                       │
│  ┌────────────────────────────────────────────┐    │
│  │  /v1/models                                │    │
│  │  /v1/chat/completions (stream & non-stream)│    │
│  │  /threads, /runs, /assistants (Agent Proto)│    │
│  └────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────┘
                     │ LangGraph SDK
                     ↓
┌─────────────────────────────────────────────────────┐
│           LangGraph Agents                          │
│  ┌──────────────┐  ┌──────────────┐                │
│  │  React Agent │  │  HITL Agent  │  ...           │
│  └──────────────┘  └──────────────┘                │
└────────────────────┬────────────────────────────────┘
                     │ State persistence
                     ↓
┌─────────────────────────────────────────────────────┐
│        PostgreSQL Database                          │
│  ├─ Agent state (checkpoints)                       │
│  ├─ Thread history                                  │
│  ├─ Assistant metadata                              │
│  └─ Run history                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment

### Docker Compose

```bash
docker compose -f docker-compose.all.yml up -d
```

Services:
- **Aegra:** http://localhost:8000
- **Chat UI:** http://localhost:3000
- **Database:** localhost:5432

### Environment Variables

```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/aegra
AUTH_TYPE=noop
PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ASSISTANT_ID=agent
LANGSMITH_API_KEY=
```

### Scale to Production

1. Replace `localhost:8000` with your domain
2. Enable authentication: `AUTH_TYPE=custom`
3. Use cloud database: `postgresql://...@cloud-db.com`
4. Deploy with Kubernetes/Railway/Heroku
5. Use CDN for frontend assets

---

## 🎓 Learning Resources

### For Backend Development
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Aegra CLAUDE.md](/home/aegra/CLAUDE.md)

### For Frontend Development
- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev/)
- [Agent Chat UI README](/home/agent-chat-ui/README.md)

### For Agent Development
- [LangChain Docs](https://python.langchain.com/)
- [Building LangGraph Agents](https://langchain-ai.github.io/langgraph/tutorials/)

---

## 💡 Common Tasks

### Add a New Agent

```bash
# 1. Create agent file
# /home/aegra/graphs/my_agent/graph.py

# 2. Export compiled graph
# graph = workflow.compile()

# 3. Register in aegra.json
{
  "graphs": {
    "my_agent": "./graphs/my_agent/graph.py:graph"
  }
}

# 4. Restart Aegra
# Agent appears in /v1/models automatically
```

### Connect to Existing LangGraph Server

```bash
# If you have a LangGraph server running on :2024
# Just change .env in agent-chat-ui:

NEXT_PUBLIC_API_URL=http://localhost:2024
NEXT_PUBLIC_ASSISTANT_ID=agent
```

### Enable API Authentication

```bash
# 1. Set AUTH_TYPE=custom in .env
# 2. Edit /home/aegra/auth.py
# 3. Implement your auth logic (Firebase, JWT, etc.)
# 4. Frontend requires API key now
```

---

## 📞 Support

### Getting Help

1. **Check documentation:** See [📖 Documentation](#-documentation) section
2. **Run tests:** `make test` to verify everything works
3. **Check logs:** `make logs` to see error messages
4. **Review code:** Check specific module docs

### Reporting Issues

Include:
- Error message (full traceback)
- What you were trying to do
- Steps to reproduce
- Your environment (OS, Python version, Node version)

---

## 🎉 What's Next?

1. ✅ **Started:** Aegra + Agent Chat UI integration
2. ✅ **Tested:** OpenAI-compatible API endpoints
3. ⏭️ **Next:** Customize agents for your use case
4. ⏭️ **Next:** Deploy to production
5. ⏭️ **Next:** Add authentication
6. ⏭️ **Next:** Monitor and scale

---

## 📝 Files Created/Modified

### Created
- ✨ `/home/agent-chat-ui/.env` - Frontend configuration
- ✨ `/home/docker-compose.all.yml` - Docker all-in-one setup
- ✨ `/home/Makefile` - Management commands
- ✨ `/home/test_integration.sh` - Integration tests
- ✨ `/home/QUICK_START.md` - 5-minute guide
- ✨ `/home/INTEGRATION_GUIDE.md` - Full documentation

### Already Existed (Ready to Use)
- `/home/aegra/src/agent_server/api/openai_compat.py` - OpenAI endpoints
- `/home/agent-chat-ui/src/providers/Stream.tsx` - Stream provider
- `/home/agent-chat-ui/.env.example` - Example config

---

## 🏁 Summary

✅ **OpenAI-compatible API** - Full endpoints for chat, models, etc.  
✅ **Agent Chat UI** - Production-ready frontend  
✅ **Multi-Agent Support** - Select any agent from dropdown  
✅ **Thread Management** - Persistent conversation memory  
✅ **Streaming** - Real-time message generation  
✅ **Authentication** - Built-in auth support  
✅ **Docker** - All-in-one deployment  
✅ **Documentation** - Complete setup guides  

---

**Status:** ✅ **Production Ready**  
**Last Updated:** November 17, 2025  
**Maintainer:** Community-driven

🚀 **Ready to build amazing AI chat applications!**
