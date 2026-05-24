# Production-Ready AI Workflow Infrastructure

Enterprise-grade multi-agent architecture powered by **Langflow**, **OpenRouter**, and **Z.ai GLM 4.5 Air**.

Repository: https://github.com/tarun89034/Advanced-Multi-Agent-Workout-App

---

## Architecture

```
Users → Cloudflare CDN/WAF → Cloudflare Tunnel → Docker Container → Langflow → OpenRouter Node → Z.ai GLM 4.5 Air (free)
```

### Model Routing Strategy

| Priority   | Model                    | Provider    | Cost |
|------------|--------------------------|-------------|------|
| Primary    | `z-ai/glm-4.5-air:free` | Z.ai        | Free |
| Fallback   | `deepseek/deepseek-chat` | DeepSeek    | Paid |
| Emergency  | `openai/gpt-4o-mini`     | OpenAI      | Paid |

All models are routed through **OpenRouter** for multi-provider resilience and reduced vendor lock-in.

---

## Quick Start

### 1. Environment Setup

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### 2. Run Locally

```bash
pip install -r requirements.txt
streamlit run main.py
```

### 3. Run with Docker

```bash
docker-compose up --build
```

The application will be available at `http://localhost:8501`.  
Langflow (optional local instance) will be at `http://localhost:7860`.

---

## Project Structure

```
├── main.py                          # Streamlit UI — enterprise infrastructure dashboard
├── ai.py                            # Async AI inference with Langflow + OpenRouter
├── custom_components/
│   └── openrouter_component.py      # Custom Langflow node with fallback routing
├── flows/
│   ├── AskAIV2.json                 # Langflow agent flow
│   └── Macro Flow.json              # Langflow macro generation flow
├── Dockerfile                       # Containerized runtime
├── docker-compose.yml               # Multi-service orchestration
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
└── .gitignore                       # Security: excludes secrets & caches
```

---

## Infrastructure Features

### Security
- Environment variable secrets management (`.env`)
- Cloudflare Access zero-trust authentication
- Rate limiting (60 req/min/IP)
- HTTPS via Cloudflare Tunnel (hidden origin IP)

### Reliability
- 3x automatic retries on transient failures
- 60s request timeouts
- Token streaming for reduced perceived latency
- Multi-provider fallback model chain

### Scalability
- Dockerized deployment with health checks
- Async HTTP via `httpx.AsyncClient`
- OpenRouter model list caching (5-minute TTL)
- Structured logging via Loguru + OpenTelemetry traces

### Observability
- **LangSmith** — Prompt traces, tool usage, generation latency
- **Sentry** — Exception catching, crash reports
- **Grafana / Prometheus** — Docker metrics, tunnel health
- **Loguru** — Rotating file logs (10 MB / 10 days retention)

---

## Cloudflare Deployment

1. Install `cloudflared`: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
2. Authenticate: `cloudflared tunnel login`
3. Create tunnel: `cloudflared tunnel create ai-workflow`
4. Route: `cloudflared tunnel route dns ai-workflow your-domain.com`
5. Run: `cloudflared tunnel run ai-workflow`

> **Important:** Never expose Docker ports directly. All traffic must flow through the Cloudflare Tunnel.

---

## License

MIT
