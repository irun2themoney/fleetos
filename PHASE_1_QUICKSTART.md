# Phase 1 Quickstart: Local OpenClaw Setup (Days 1-2)

**Status:** You're here 🎯  
**Goal:** Get OpenClaw, Ollama, and Telegram working locally  
**Timeline:** 2 days  
**Difficulty:** Beginner-friendly

---

## 📋 Phase 1 Checklist

- [ ] Clone repository locally
- [ ] Setup Python virtual environment
- [ ] Install dependencies
- [ ] Start Docker services (Ollama, Redis, Chroma)
- [ ] Configure Ollama with Llama 3.1 70B
- [ ] Setup Telegram bot and integration
- [ ] Test single agent with CLI
- [ ] Document any issues for Phase 2

---

## 🚀 Step-by-Step Setup (45 minutes)

### Step 1: Clone Repository (5 min)

After you push to GitHub:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/fleetos.git
cd fleetos

# Verify you're in the right place
ls -la
```

You should see all 25+ files including README.md, docker-compose.yml, etc.

### Step 2: Setup Python Environment (5 min)

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
which python
```

### Step 3: Install Dependencies (10 min)

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation (should show versions, no errors)
pip list | head -20
```

### Step 4: Start Docker Services (10 min)

```bash
# Start all services in background
docker-compose up -d

# Wait 30 seconds for services to boot
sleep 30

# Check service status
docker-compose ps

# You should see 5 services:
# - ollama (LLM inference) — Port 11434
# - redis (caching) — Port 6379
# - chroma (vector DB) — Port 8000
# - fleetos (main app) — Port 8501
```

If services fail to start:
```bash
# Check logs
docker-compose logs ollama
docker-compose logs redis
docker-compose logs chroma

# Rebuild if needed
docker-compose down
docker-compose build
docker-compose up -d
```

### Step 5: Configure Ollama (10 min)

```bash
# Wait for Ollama to be ready
curl http://localhost:11434/api/tags

# Pull Llama 3.1 70B (takes 5-10 minutes, ~45GB)
ollama pull llama3.1:70b

# Verify it's downloaded
ollama list
```

If your machine doesn't have 45GB:
```bash
# Use smaller model instead
ollama pull llama3.1:13b  # ~8GB
ollama pull dolphin-mixtral:8x7b  # ~26GB
```

Update `.env`:
```bash
# Edit .env and change:
OLLAMA_MODEL=llama3.1:13b
```

### Step 6: Setup Telegram (10 min - Optional for Phase 1)

To enable human approval gates, you'll need Telegram:

1. **Create Telegram Bot**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Type `/newbot`
   - Follow prompts
   - Copy the **API token**

2. **Get Your Chat ID**
   - Start a chat with your new bot
   - Message it something
   - Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find your `chat_id` in the response

3. **Update .env**
   ```bash
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

4. **Test it works**
   ```bash
   python3 -c "
   import os
   from dotenv import load_dotenv
   load_dotenv()
   token = os.getenv('TELEGRAM_BOT_TOKEN')
   print('✓ Telegram configured!' if token else '✗ Token missing')
   "
   ```

---

## ✅ Verify Phase 1 Setup

### Test 1: CLI Help (30 seconds)

```bash
python -m fleetos.cli --help

# Should show:
# Usage: cli.py [OPTIONS] COMMAND [ARGS]
# Commands:
#   configure  Interactive configuration wizard
#   run        Run a FleetOS command
#   search     Search company memory
#   status     Show FleetOS status
```

### Test 2: Check Status (30 seconds)

```bash
python -m fleetos.cli status

# Should show:
# FleetOS Status
# ================
# Artifacts stored: 0
# Relationships: 0
# Timestamp: 2026-03-04T...
```

### Test 3: Run a Simple Command (1-2 minutes)

```bash
python -m fleetos.cli run "Tell me about yourself"

# Should show:
# ✓ Decomposed into 4 roles
#   - Strategy
#   - Content
#   - Marketing
#   - Sales
# ✓ Fleet execution completed
#   Artifacts: 4
#   Errors: 0
```

### Test 4: Search Memory (30 seconds)

```bash
python -m fleetos.cli search "yourself"

# Should show search results from the previous command
```

---

## 🐛 Troubleshooting Phase 1

### Issue: Docker services won't start

```bash
# Check Docker is running
docker ps

# Rebuild and restart
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Ollama is slow

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
docker-compose restart ollama

# Wait 2 minutes for restart
sleep 120
```

### Issue: Python import errors

```bash
# Verify virtual environment is active
which python

# Should show: /path/to/fleetos/venv/bin/python

# If not, activate it:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Not enough disk space

```bash
# Check available space
df -h

# If < 50GB, use smaller Ollama model:
ollama pull llama3.1:13b
# Then update .env: OLLAMA_MODEL=llama3.1:13b
```

---

## 📚 What You've Accomplished

By the end of Phase 1, you'll have:

✅ **Local FleetOS running**
- Python package installed and tested
- CLI interface working
- All 4 commands functional

✅ **Infrastructure up**
- Docker Compose with 5 services
- Ollama running LLM locally
- Redis caching configured
- Chroma vector database ready

✅ **Telegram notifications ready** (optional)
- Approval flow configured
- Human-in-the-loop gates available

✅ **Documentation**
- Project specification read
- Architecture understood
- CLI tested and working

---

## 🎯 Next: Phase 2 (Days 3-5)

Once Phase 1 is working, you'll:

1. **Integrate real OpenClaw** agents
2. **Implement LangGraph DAG** orchestration
3. **Get 4 agents running in parallel**
4. **Aggregate results and test end-to-end**

See `FleetOS_Project_Specification.docx` Phase 2 section for details.

---

## 💡 Pro Tips

1. **Keep Docker running**
   - Leave `docker-compose up` running during development
   - Check logs anytime: `docker-compose logs -f service_name`

2. **Use Python REPL for quick tests**
   ```bash
   python3
   >>> from fleetos.core.planner import Planner
   >>> planner = Planner()
   >>> agents = planner.decompose("my command", {})
   ```

3. **Monitor Ollama**
   - Visit http://localhost:11434 to see Ollama status
   - Check logs: `docker-compose logs ollama`

4. **Save progress**
   - Commit daily: `git add . && git commit -m "Day 1: Phase 1 setup"`
   - Push to GitHub: `git push origin main`

---

## ⏱️ Time Budget

- Setup: 45 minutes
- Testing: 15 minutes
- Troubleshooting (if needed): 30 minutes
- **Total: ~1-2 hours for full Phase 1 setup**

---

## ✨ Success Criteria

Phase 1 is complete when:

- [x] Docker services running: `docker-compose ps` (all healthy)
- [x] Ollama working: `curl http://localhost:11434/api/tags` (returns models)
- [x] CLI functional: `python -m fleetos.cli --help` (shows commands)
- [x] Test command passes: `python -m fleetos.cli run "test"` (no errors)
- [x] Memory working: `python -m fleetos.cli status` (shows artifacts)

**Once all boxes are checked, you're ready for Phase 2! 🎉**

---

**Next:** Read `PHASE_2_DEEP_DIVE.md` (coming soon) for detailed Phase 2 planning.

