# FleetOS + OpenClaw

> Kubernetes-style orchestration for solo founder autonomous businesses

**Goal:** Build a superior, free/local-first version of FleetOS — the orchestration layer on top of OpenClaw — so a solo founder can type one natural-language command and spin up a full autonomous business (newsletter → $15k MRR, lead-gen agency, micro-SaaS, etc.).

**Status:** 100% buildable today (March 2026) with open-source tools. Local MVP in 7–14 days. Cloud-scalable MVP in 30–45 days. Zero to minimal cost.

---

## 🎯 Vision

Imagine typing:
```
fleetos run "Launch my premium newsletter targeting indie hackers, $15k MRR in 90 days"
```

And FleetOS automatically:
- ✅ Spins up a **Strategy Agent** to define your positioning & pricing
- ✅ Spawns a **Content Agent** to write your launch emails & posts
- ✅ Launches a **Marketing Agent** to execute LinkedIn/Twitter outreach
- ✅ Kicks off a **Sales Agent** to follow up with warm leads
- ✅ Runs a **Finance Agent** to track revenue & metrics
- ✅ Manages a **Support Agent** for customer questions
- ✅ Maintains a shared knowledge graph so agents learn from each other
- ✅ Routes risky actions (e.g., send 10k cold emails) to you for approval
- ✅ Evolves by analyzing past failures and auto-generating new agent skills

All without hiring a single person.

---

## 🛠️ Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Worker Runtime** | OpenClaw | Ready-made AgentSkills, Telegram/WhatsApp support, local execution |
| **Orchestration** | LangGraph | Hierarchical planning, stateful DAGs, composable agents |
| **Scaling** | Minikube / Docker Compose | Free local K8s-like fleets |
| **Memory** | Chroma + Redis + GraphRAG | Persistent company knowledge graph |
| **Dashboard** | Streamlit | Real-time Starcraft-style command center |
| **Verification** | Custom LangGraph nodes | VerdictNet-style confidence scoring + human gates |
| **LLM** | Ollama (Llama 3.1 70B / Qwen2.5) | Completely free & local |
| **Deployment** | Docker + Oracle Always Free | Zero-cost scaling |

---

## 📁 Project Structure

```
fleetos/
├── README.md
├── requirements.txt
├── docker-compose.yml
│
├── fleetos/
│   ├── __init__.py
│   ├── core/
│   │   ├── planner.py          # LangGraph high-level decomposer
│   │   ├── orchestrator.py     # Spawns OpenClaw instances
│   │   ├── memory.py           # Shared GraphRAG + Chroma
│   │   └── verifier.py         # VerdictNet critic node
│   │
│   ├── agents/
│   │   └── openclaw_wrapper.py # Wrapper around OpenClaw CLI/API
│   │
│   ├── dashboard/
│   │   └── app.py              # Streamlit command center
│   │
│   ├── templates/              # Business templates (JSON + prompts)
│   │   ├── newsletter_v1.json
│   │   └── leadgen_agency_v1.json
│   │
│   └── cli.py                  # Main CLI entrypoint
│
├── skills/                     # Custom OpenClaw skills
├── k8s/                        # Kubernetes CRDs (production)
└── tests/                      # Unit + integration tests
```

---

## 🚀 8-Phase Development Roadmap

### Phase 1: Local OpenClaw Setup (Days 1–2)
**Objective:** Get OpenClaw running locally with Ollama and messaging.

- [ ] Clone OpenClaw & install dependencies
- [ ] Download Ollama and pull Llama 3.1 70B
- [ ] Configure Telegram/WhatsApp
- [ ] Test: `openclaw run "What is my Stripe balance?"`

**Deliverable:** Working single-agent in isolation

---

### Phase 2: Basic Fleet Orchestration (Days 3–5)
**Objective:** Build planner and orchestrator to spawn parallel agent workers.

- [ ] Implement `fleetos/core/planner.py` (LangGraph planner node)
- [ ] Implement `fleetos/core/orchestrator.py` (spawn OpenClaw instances)
- [ ] Build LangGraph DAG: input → planner → parallel workers → aggregator
- [ ] Test: Single command spawns 4 agents in parallel

**Deliverable:** 4-agent fleet with coordinated execution

---

### Phase 3: Persistent Memory & Evolution (Days 6–8)
**Objective:** Build knowledge graph and auto-skill generation.

- [ ] Implement `fleetos/core/memory.py` (Chroma + Redis)
- [ ] Integrate GraphRAG for knowledge graph updates
- [ ] Implement feedback loop: analyze failures → auto-generate skills
- [ ] Test: Agents share context, fleet improves over time

**Deliverable:** Stateful fleet with persistent learning

---

### Phase 4: Command Center Dashboard (Days 9–11)
**Objective:** Build Streamlit UI for fleet monitoring.

- [ ] Implement `fleetos/dashboard/app.py`
- [ ] Display live agent status (role, activity, last artifact)
- [ ] Add "Spin New Fleet" button
- [ ] Test: Dashboard reflects real-time activity

**Deliverable:** Real-time visualization of fleet operations

---

### Phase 5: VerdictNet Verification Layer (Days 12–14)
**Objective:** Add confidence scoring and human approval gates.

- [ ] Implement `fleetos/core/verifier.py` (critic node)
- [ ] Score agent outputs (0–100 confidence)
- [ ] Route low-confidence actions to Telegram for approval
- [ ] Test: Risky actions require human sign-off

**Deliverable:** Human-in-loop governance

---

### Phase 6: Business Templates (Days 15–20)
**Objective:** Pre-built templates for common archetypes.

- [ ] Define template schema (roles, tools, prompts, rules)
- [ ] Create `newsletter_v1.json` template
- [ ] Create `leadgen_agency_v1.json` template
- [ ] Implement template matcher (NL → template selection)
- [ ] Test: Single command loads complete business setup

**Deliverable:** One-command business launch

---

### Phase 7: Cloud Scaling (Days 21–30)
**Objective:** Deploy to cloud with Kubernetes.

- [ ] Create `k8s/` CRDs for kagent
- [ ] Build `docker-compose.yml` for local multi-node testing
- [ ] Deploy to Oracle Always Free or Google Cloud free tier
- [ ] Test: Fleet scales with zero code changes

**Deliverable:** Production-ready cloud infrastructure

---

### Phase 8: Polish & Launch (Days 31–45)
**Objective:** Finalize MVP and open-source.

- [ ] Implement self-evolution loop
- [ ] Polish CLI and dashboard UX
- [ ] Create landing page and waitlist
- [ ] Plan first paid tier (hosted cloud fleets + enterprise governance)

**Deliverable:** Open-source release ready for community

---

## 📊 Success Metrics

| Milestone | Criteria | Timeline |
|-----------|----------|----------|
| **MVP (Phase 2)** | 4 agents spawn, complete tasks, artifacts aggregated | Day 5 |
| **Full MVP (Phase 6)** | Newsletter template fully operational, all integrations working | Day 20 |
| **Production (Phase 7)** | Fleet runs on free tier, scales to cloud, $0 cost | Day 30 |
| **Launch (Phase 8)** | 1000+ GitHub stars, 100+ waitlist signups | Day 45 |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ User Interface: CLI (click) + Streamlit Dashboard          │
├─────────────────────────────────────────────────────────────┤
│ Orchestration Layer: LangGraph Planner + Orchestrator      │
├─────────────────────────────────────────────────────────────┤
│ Verification & Routing: VerdictNet Critic + Gates          │
├─────────────────────────────────────────────────────────────┤
│ Agent Workers: OpenClaw instances (Parallel execution)     │
├─────────────────────────────────────────────────────────────┤
│ Memory & Knowledge: Chroma + Redis + GraphRAG              │
├─────────────────────────────────────────────────────────────┤
│ LLM & Inference: Ollama (Llama 3.1 70B / Qwen2.5)           │
├─────────────────────────────────────────────────────────────┤
│ Integrations: Stripe, ConvertKit, Twitter, Gmail, etc.     │
├─────────────────────────────────────────────────────────────┤
│ Deployment: Docker + Kubernetes (local/cloud)              │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- 16GB+ RAM (for local LLM inference)
- Git

### Phase 1 Setup (Days 1–2)

```bash
# 1. Clone this repo
git clone https://github.com/yourusername/fleetos.git
cd fleetos

# 2. Install FleetOS
pip install -r requirements.txt

# 3. Install Ollama
curl https://ollama.ai/install.sh | sh

# 4. Pull LLM
ollama pull llama3.1:70b

# 5. Start Ollama (in background)
ollama serve &

# 6. Configure Telegram (interactive)
fleetos configure --telegram

# 7. Test single agent
fleetos test-agent "What is 2+2?"
```

### Phase 2 Setup (Days 3–5)

```bash
# Start dashboard
streamlit run fleetos/dashboard/app.py

# Run orchestrator with 4 agents
fleetos run "Analyze my business model and suggest growth strategies"
```

### Phase 6 (One-Command Magic)

```bash
# Launch complete newsletter business
fleetos run "Launch my premium newsletter targeting indie hackers, $15k MRR in 90 days"
```

---

## 🔌 Integrations (Phase 6+)

Pre-built OpenClaw skills for:
- **Payments:** Stripe (balance, charges, customers)
- **Email:** ConvertKit, Substack, Mailchimp
- **Social:** Twitter, LinkedIn, TikTok
- **Analytics:** Google Analytics, Mixpanel
- **Support:** Intercom, Zendesk
- **Automation:** Zapier, Make (Integromat)

Add custom integrations via `skills/` directory.

---

## 🤖 Example: Newsletter Business

**One-liner:**
```
fleetos run "Launch my premium newsletter targeting indie hackers, $15k MRR in 90 days"
```

**What FleetOS does:**

1. **Strategy Agent** drafts positioning, pricing, target customer profile
2. **Content Agent** writes launch emails, welcome sequences, sample issues
3. **Marketing Agent** executes Twitter/LinkedIn outreach, cold emails
4. **Sales Agent** follows up with warm leads, books calls
5. **Finance Agent** sets up Stripe, tracks metrics, forecasts revenue
6. **Support Agent** creates FAQ, response templates, escalation rules

All agents share context via persistent knowledge graph. Low-confidence actions (e.g., "send 10k cold emails") route to you for approval via Telegram.

**Timeline:** 48 hours to first customer. 90 days to $15k MRR.

---

## 📚 Documentation

- **[Project Specification](./docs/FleetOS_Project_Specification.docx)** – Detailed tech specs & development phases
- **[Implementation Checklist](./docs/FleetOS_Implementation_Checklist.xlsx)** – Step-by-step task list
- **[Architecture Design](./docs/FleetOS_Architecture_Design.docx)** – System architecture & data flow

---

## 🤝 Contributing

FleetOS is open-source and welcomes contributions!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

## 📜 License

MIT License – See [LICENSE](./LICENSE) file for details.

---

## 🙋 Questions?

- **GitHub Issues:** Report bugs and request features
- **Discussions:** Ask questions and share ideas
- **Email:** contact@fleetos.dev

---

**Built with ❤️ for solo founders who want to build like a team.**
