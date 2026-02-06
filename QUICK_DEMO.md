# Sovereign Sentinel - Quick Demo Reference

## 🚀 Start System (2 Terminals)

**Terminal 1 - Backend:**
```bash
cd Sovereign-Sentinel/backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd Sovereign-Sentinel/frontend
npm run dev
```

**Access:** http://localhost:3000

## ⚡ Quick Demo Commands

### 1. OSINT Scout (Geopolitical Monitoring)
```bash
# Get current risk score
curl http://localhost:8000/api/risk/latest

# Trigger scan
curl -X POST http://localhost:8000/api/scan/immediate
```

### 2. Forensic Auditor (PIK Loan Analysis)
```bash
cd Sovereign-Sentinel/backend
python test_forensic_auditor_demo.py
```

### 3. Policy Brain (Risk Orchestration)
```bash
cd Sovereign-Sentinel/backend
python test_policy_brain_demo.py
```

### 4. Voice Alert System
```bash
# Trigger audio alert
curl -X POST http://localhost:8000/api/test/broadcast-mock-alert

# Then open http://localhost:3000 to see/hear it
```

### 5. Treasury Commander (Autonomous Trading)
```bash
# Execute mock hedge
curl -X POST http://localhost:8000/api/test/execute-mock-hedge

# View agent reasoning
curl http://localhost:8000/api/hedge/agent-memory
```

## 🎬 5-Minute Demo Flow

1. **Open Dashboard** → http://localhost:3000
2. **Trigger Alert** → `curl -X POST http://localhost:8000/api/test/broadcast-mock-alert`
3. **See Audio Alert** → Audio player appears, auto-plays
4. **Click APPROVE** → Authorization recorded
5. **Execute Hedge** → `curl -X POST http://localhost:8000/api/test/execute-mock-hedge`
6. **Show Result** → 33.33 BTC purchased, $1.5M hedge executed

## 📊 What Each Component Does

| Component | What It Does | Demo Command |
|-----------|--------------|--------------|
| **OSINT Scout** | Monitors global crises every 15 min | `curl http://localhost:8000/api/risk/latest` |
| **Forensic Auditor** | Detects PIK toggles with AI | `python test_forensic_auditor_demo.py` |
| **Policy Brain** | Evaluates risk & escalates | `python test_policy_brain_demo.py` |
| **Voice Alert** | Audio notifications for critical alerts | `curl -X POST .../broadcast-mock-alert` |
| **Treasury Commander** | Executes BTC hedges autonomously | `curl -X POST .../execute-mock-hedge` |
| **Dashboard** | Real-time monitoring & control | http://localhost:3000 |

## 🎯 Key Features to Highlight

✅ **Real-time Monitoring** - WebSocket updates every 15 minutes
✅ **AI-Powered Analysis** - OpenAI reasoning for PIK detection
✅ **Voice Alerts** - Auto-play audio with approve/dismiss
✅ **Autonomous Trading** - Multi-step hedge execution with self-verification
✅ **Full Transparency** - Agent reasoning traces at every step
✅ **Self-Learning** - Policy Brain learns from human overrides

## 📈 Demo Results

**OSINT Scout:**
- Risk Score: 0-100 (updates every 15 min)
- Sectors: energy, currency, sovereign
- Articles: 10+ with sentiment analysis

**Forensic Auditor:**
- Analyzes: CSV/JSON loan portfolios
- Detects: PIK toggles (Cash → PIK)
- Flags: High-risk loans with confidence scores

**Voice Alert:**
- Generates: Audio via OpenAI TTS
- Delivers: WebSocket to dashboard
- Fallback: Email if TTS fails

**Treasury Commander:**
- Calculates: Hedge amount (15% of $10M = $1.5M)
- Executes: BTC purchase (33.33 BTC @ $45k)
- Verifies: Order status and confirms fill
- Reports: Human-readable trade summary

## 🔧 Troubleshooting

**Backend not starting?**
```bash
pkill -f "uvicorn app.main:app"
cd Sovereign-Sentinel/backend
uvicorn app.main:app --reload
```

**Frontend not starting?**
```bash
cd Sovereign-Sentinel/frontend
npm install
npm run dev
```

**Audio not playing?**
- Check browser audio permissions
- Use mock alert: `curl -X POST http://localhost:8000/api/test/broadcast-mock-alert`

## 📞 Quick Links

- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Full Demo Guide: `DEMO_GUIDE.md`

---

**Status:** ✅ Ready to Demo
**Time:** 5-10 minutes
**Wow Factor:** 🚀🚀🚀
