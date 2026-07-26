# Advanced Multi-Agent Workout App

Enterprise-grade multi-agent AI infrastructure for personalized fitness, nutrition planning, and intelligent workout assistance.

Built using Streamlit, Langflow, OpenRouter, Astra DB, and Z.ai GLM 4.5 Air.

Demo Video

https://res.cloudinary.com/dgbobo43l/video/upload/v1784119929/ai-workout-multiagent_nhbbn2.mp4

---

# Overview

This project is a sophisticated multi-agent AI application that helps users manage fitness profiles, nutrition goals, personal notes, and AI-generated workout recommendations through a production-ready AI orchestration stack.

The system combines:

* Langflow multi-agent orchestration
* Retrieval-Augmented Generation (RAG)
* Vector search with Astra DB
* OpenRouter multi-provider model routing
* Cloudflare-secured deployment
* Dockerized infrastructure
* Streamlit interactive frontend

The platform is designed as a scalable, enterprise-oriented AI infrastructure layer for intelligent fitness and wellness applications.

---

# Architecture

```text
Users
  ↓
Cloudflare CDN / WAF
  ↓
Cloudflare Tunnel
  ↓
Docker Container
  ↓
Streamlit Frontend
  ↓
Langflow Multi-Agent Flows
  ↓
Custom OpenRouter Node
  ↓
AI Model Routing Layer
  ├── Z.ai GLM 4.5 Air (Primary)
  ├── DeepSeek Chat (Fallback)
  └── GPT-4o Mini (Emergency)
```

---

# Core Features

## Multi-Agent AI Flows

The application uses Langflow to orchestrate advanced multi-agent workflows capable of:

* task routing between models
* dynamic reasoning chains
* tool-calling agents
* prompt orchestration
* fallback model switching
* contextual retrieval workflows

Langflow JSON flows are exported and executed locally or through API-driven inference pipelines.

---

## AI-Driven Personalization

The platform automatically generates:

* calorie targets
* protein requirements
* fat goals
* carbohydrate targets
* personalized workout recommendations

based on:

* user profile metrics
* weight
* height
* activity level
* fitness goals
* nutrition objectives

---

## Conversational AI Assistant

The built-in "Ask AI" assistant provides:

* context-aware fitness advice
* nutrition recommendations
* workout guidance
* profile-aware responses
* semantic memory retrieval

The assistant synthesizes:

* user profile information
* stored notes
* retrieved vector memories
* general fitness knowledge
* AI reasoning chains

through Langflow-powered tool-calling agents.

---

## Retrieval-Augmented Generation (RAG)

The project implements a full RAG pipeline using Astra DB vector search.

Capabilities include:

* semantic note retrieval
* persistent memory
* vector similarity search
* contextual AI responses
* long-term user knowledge storage

User notes are embedded and stored in Astra DB to provide memory-aware AI interactions.

---

## Dynamic Streamlit UI

The frontend is built with Streamlit and includes:

* interactive forms
* persistent session state
* profile management
* nutrition dashboards
* notes management
* conversational AI interface
* workflow visualization

The UI is optimized for responsive interaction with real-time AI inference.

---

# AI Model Routing Strategy

| Priority  | Model                    | Provider | Purpose                |
| --------- | ------------------------ | -------- | ---------------------- |
| Primary   | `z-ai/glm-4.5-air:free`  | Z.ai     | Primary inference      |
| Fallback  | `deepseek/deepseek-chat` | DeepSeek | Reliability fallback   |
| Emergency | `openai/gpt-4o-mini`     | OpenAI   | Critical recovery path |

All providers are accessed through OpenRouter for:

* provider abstraction
* multi-model resilience
* vendor independence
* centralized API routing
* simplified infrastructure management

---

# Technology Stack

## Frontend

* Streamlit

## AI Orchestration

* Langflow
* LangChain

## LLM Infrastructure

* OpenRouter
* Z.ai GLM 4.5 Air
* DeepSeek
* OpenAI GPT-4o Mini

## Vector Database

* Astra DB

## Embeddings

* Nvidia Embedding Models

## Infrastructure

* Docker
* Docker Compose
* Cloudflare Tunnel
* Cloudflare WAF

## Monitoring & Observability

* LangSmith
* Sentry
* OpenTelemetry
* Loguru
* Grafana
* Prometheus

---

# Repository Structure

```text
.
├── main.py
├── ai.py
├── custom_components/
│   └── openrouter_component.py
├── flows/
│   ├── AskAIV2.json
│   └── Macro Flow.json
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── .gitignore
```

---

# Infrastructure Features

## Security

### Environment Variable Secret Management

Sensitive credentials are stored securely using environment variables.

Supported secrets include:

* OpenRouter API keys
* Astra DB credentials
* LangSmith tokens
* Sentry DSNs

---

## Cloudflare Zero-Trust Deployment

Infrastructure is protected using:

* Cloudflare Tunnel
* Cloudflare WAF
* Cloudflare Access
* HTTPS enforcement
* hidden origin architecture

---

## Rate Limiting

Production traffic protection includes:

```text
60 requests/minute/IP
```

to prevent abuse and excessive inference costs.

---

# Reliability Engineering

## Automatic Retry Logic

The AI inference pipeline includes:

```text
3x automatic retries
```

for transient failures and provider instability.

---

## Timeout Protection

All inference requests are protected using:

```text
60-second request timeouts
```

to prevent hanging workflows and stalled agents.

---

## Streaming Responses

Token streaming is enabled to reduce perceived latency and improve user experience.

---

## Multi-Provider Failover

Inference automatically falls back across providers if upstream models fail or become unavailable.

---

# Scalability

## Async AI Requests

Inference is powered through:

```python
httpx.AsyncClient
```

to improve throughput and concurrency.

---

## Dockerized Deployment

The platform supports containerized deployment using:

* Docker
* Docker Compose

allowing consistent local and production environments.

---

## Cached Model Discovery

OpenRouter model metadata is cached to reduce API overhead and improve Langflow responsiveness.

---

# Observability & Monitoring

## LangSmith

Tracks:

* prompt traces
* tool execution
* chain latency
* agent workflows

---

## Sentry

Captures:

* runtime exceptions
* deployment failures
* crash reports
* infrastructure errors

---

## Grafana & Prometheus

Provides infrastructure monitoring for:

* Docker containers
* AI service health
* system metrics
* Cloudflare tunnel health

---

## Structured Logging

Loguru provides:

* rotating log files
* structured JSON logs
* debugging traces
* long-term retention

Configuration:

```text
10 MB rotation
10-day retention
```

---

# Local Development Setup

## 1. Clone Repository

```bash
git clone https://github.com/tarun89034/Advanced-Multi-Agent-Workout-App.git

cd Advanced-Multi-Agent-Workout-App
```

---

## 2. Create Environment Variables

```bash
cp .env.example .env
```

Populate `.env`:

```env
OPENROUTER_API_KEY=
ASTRA_DB_API_ENDPOINT=
ASTRA_DB_APPLICATION_TOKEN=
LANGSMITH_API_KEY=
SENTRY_DSN=
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run Streamlit App

```bash
streamlit run main.py
```

Application URL:

```text
http://localhost:8501
```

Optional Langflow instance:

```text
http://localhost:7860
```

---

# Docker Deployment

## Build and Run

```bash
docker-compose up --build
```

---

# Langflow Integration

The application uses Langflow as the orchestration layer for:

* multi-agent workflows
* AI routing
* tool calling
* prompt chains
* RAG pipelines
* conversational agents

Flows are exported as JSON configurations and executed locally through Python integrations.

---

# Astra DB Integration

Astra DB is configured with vectorization support to enable:

* semantic retrieval
* persistent memory
* contextual AI responses
* note embedding search

The vector database powers the RAG memory system used by conversational agents.

---

# Engineering Notes

## ImportError Resolution

A previous import issue involving `create_profile` was resolved through:

* clearing Python bytecode cache
* rebuilding `profiles.py`
* validating exports
* verifying import paths

This eliminated stale cache corruption and restored clean runtime imports.

---

# Known Runtime Notes

Some third-party library warnings may appear during startup, including:

* `transformers` namespace warnings
* `astrapy` SSL reuse notices
* LangChain deprecation warnings

These warnings are upstream dependency notices and do not affect application functionality.

---

# Future Improvements

Planned upgrades include:

* Kubernetes deployment support
* distributed inference workers
* persistent conversation history
* advanced RAG pipelines
* CI/CD automation
* multi-user authentication
* RBAC permissions
* production analytics dashboards
* model performance benchmarking

---

# License

This project is intended for educational, research, and experimental AI infrastructure purposes.

---

# Acknowledgements

Built using:

* Langflow
* LangChain
* OpenRouter
* Streamlit
* Astra DB
* Cloudflare
* OpenTelemetry

---

# Repository

GitHub Repository:

https://github.com/tarun89034/Advanced-Multi-Agent-Workout-App
