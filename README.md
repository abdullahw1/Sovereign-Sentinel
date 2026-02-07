# 🛡️ Sovereign Sentinel

**AI-Powered Financial War Room for Shadow Default Detection**

A multi-agent system that detects hidden credit risks before they become defaults, using real-time geopolitical intelligence, forensic loan analysis, and autonomous risk management.

---

## 🎯 The Problem

Banks lose billions to "shadow defaults" - companies that haven't officially defaulted but show critical distress signals:
- **PIK Toggles**: Borrowers switching from cash to payment-in-kind (can't afford cash payments)
- **Hidden Correlations**: Geopolitical events triggering cascading loan failures
- **Delayed Detection**: Traditional systems miss early warning signs

**Sovereign Sentinel solves this with 5 autonomous AI agents working 24/7.**

---

## 🤖 Multi-Agent Architecture

### 1. 🌍 OSINT Scout
- Monitors global news via You.com API
- Tracks geopolitical crises, energy shocks, currency volatility
- Generates real-time risk scores (0-100)

### 2. 🔬 Forensic Auditor
- Analyzes loan portfolios with OpenAI reasoning
- Detects PIK toggles by comparing historical payment data
- Flags high-risk loans with confidence scores

### 3. 🧠 Policy Brain
- Correlates geopolitical risks with loan exposure
- Evolves policies through continuous learning
- Stores human overrides in "reasoning bank" for future decisions

### 4. 🔊 Voice Alert System
- Generates audio alerts via OpenAI TTS
- Broadcasts critical warnings to dashboard
- Requires human authorization for major actions

### 5. 💰 Treasury Commander
- Executes Bitcoin hedges via Composio
- Multi-step verification with self-reasoning
- Tracks all decisions in agent memory

---

## � Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### One-Click Deployment
1. Click the button above or go to [Render Dashboard](https://dashboard.render.com/)
2. Connect your GitHub repository
3. Render will auto-detect `render.yaml` and create both services
4. Add environment variables:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `YOU_API_KEY` - Your You.com API key
5. Wait 5-10 minutes for deployment
6. Visit your frontend URL and start analyzing!

**See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.**

---

## 📊 6 Priority Credit Metrics

Sovereign Sentinel calculates industry-standard credit scores:

| Metric | What It Measures | Scoring |
|--------|------------------|---------|
| **DSCR** | Debt service coverage | 0-100 based on cash flow cushion |
| **Debt-to-Equity** | Leverage ratio | 0-100 based on capital structure |
| **Current Ratio** | Short-term liquidity | 0-100 based on ability to pay bills |
| **Interest Coverage** | Can they cover interest? | 0-100 based on EBITDA/Interest |
| **Net Profit Margin** | Profitability | 0-100 based on net income % |
| **Altman Z-Score** | Bankruptcy prediction | Safe/Grey/Distress zones |

**Overall Credit Score**: Weighted average of all 6 metrics

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- OpenAI API Key
- You.com API Key
- Composio API Key (optional)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your API keys to .env

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install

# Configure environment
cp .env.example .env.local
# Add NEXT_PUBLIC_API_URL=http://localhost:8000

# Run frontend
npm run dev
```

### 3. Access Dashboard

Open http://localhost:3000

---

## 💡 Key Features

### ✅ Real-Time Risk Monitoring
- Automated geopolitical scans every 30 minutes
- WebSocket updates to dashboard
- Live agent activity logs

### ✅ Custom Company Analysis
- Upload financial statements (Income, Balance Sheet, Cash Flow)
- Industry-specific risk research
- AI-powered recommendations

### ✅ PIK Toggle Detection
- Compares historical payment data
- Identifies borrowers in distress
- Calculates confidence scores

### ✅ Continuous Learning
- Stores human overrides in reasoning bank
- Proposes policy updates based on patterns
- Evolves risk thresholds over time

### ✅ Autonomous Hedging
- Executes Bitcoin hedges after authorization
- Multi-step verification process
- Full audit trail of decisions

---

## 📁 Project Structure

```
Sovereign-Sentinel/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── osint_scout.py       # Geopolitical intelligence
│   │   ├── forensic_auditor.py  # Loan analysis
│   │   ├── policy_brain.py      # Risk correlation
│   │   ├── voice_alert.py       # TTS alerts
│   │   ├── treasury_commander.py # Hedge execution
│   │   ├── company_analyzer.py  # Custom company analysis
│   │   └── models.py            # Pydantic models
│   ├── data/                    # Sample data & outputs
│   └── tests/                   # Test suite
├── frontend/
│   ├── app/                     # Next.js pages
│   ├── components/              # React components
│   │   ├── CommandCenter.tsx   # Agent control panel
│   │   ├── CompanyAnalysisPanel.tsx
│   │   ├── AgentChatLog.tsx
│   │   └── ...
│   └── lib/                     # API client & WebSocket
├── DEMO_GUIDE.md               # 15-minute demo walkthrough
├── QUICK_DEMO.md               # 5-minute quick reference
└── 3_MINUTE_DEMO_SCRIPT.md     # Presentation script
```

---

## 🎬 Demo Scenarios

### Scenario 1: Detect PIK Toggle
1. Click "Forensic Auditor" in Command Center
2. System analyzes 5 loans
3. Flags 2 companies that switched from Cash → PIK
4. Shows $40M total exposure

### Scenario 2: Custom Company Analysis
1. Go to "Custom Company Analysis"
2. Click "Load Sample Data" (TechFlow Solutions)
3. Click "Analyze Company"
4. See 6 credit metrics + AI recommendations

### Scenario 3: Full Workflow
1. Click "Run All" in Command Center
2. Watch 5 agents execute in sequence:
   - OSINT Scout → Forensic Auditor → Policy Brain → Voice Alert → Treasury Commander
3. See real-time logs and results

---

## 🔧 Configuration

### Environment Variables

**Backend (.env)**:
```bash
OPENAI_API_KEY=sk-...
YOU_API_KEY=...
COMPOSIO_API_KEY=ak_...  # Optional
SCAN_INTERVAL_MINUTES=30
LOG_LEVEL=INFO
```

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 API Endpoints

### Core Endpoints
- `GET /health` - System health check
- `GET /api/risk/latest` - Latest risk assessment
- `POST /api/scan/immediate` - Trigger OSINT scan

### Agent Endpoints
- `POST /api/forensic/analyze` - Run forensic analysis
- `POST /api/policy/evaluate` - Evaluate risk correlation
- `POST /api/company/analyze` - Analyze custom company
- `POST /api/hedge/execute` - Execute Bitcoin hedge

### WebSocket
- `WS /ws` - Real-time updates (risk scores, alerts, logs)

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Test individual agents
python test_forensic_auditor.py
python test_policy_brain_demo.py
python test_voice_alert.py
```

---

## 🏗️ Technology Stack

### Backend
- **FastAPI** - High-performance async API
- **OpenAI GPT-4** - Multi-step reasoning & analysis
- **You.com API** - Real-time news intelligence
- **Composio** - Trading execution
- **Pydantic** - Data validation
- **WebSockets** - Real-time updates

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **WebSocket Client** - Live updates

### Infrastructure
- **Uvicorn** - ASGI server
- **Python 3.12** - Backend runtime
- **Node.js 18** - Frontend runtime

---

## 📈 Continuous Learning

Sovereign Sentinel learns from every human override:

1. **User overrides risk score** → System extracts reasoning
2. **Stores in reasoning bank** → Builds pattern database
3. **Proposes policy updates** → "3 overrides detected, suggest raising threshold"
4. **User approves/rejects** → System adapts

This creates a **self-improving risk engine** that gets smarter over time.

---

## 🎯 Use Cases

### For Commercial Banks
- Monitor loan portfolios for early distress signals
- Detect PIK toggles before defaults
- Automate risk reporting

### For Investment Firms
- Track credit exposure across geopolitical events
- Hedge portfolio risk automatically
- Generate lending recommendations

### For Regulators
- Monitor systemic risk patterns
- Identify concentration risks
- Track shadow banking activity

---

## 🤝 Contributing

This is a hackathon project. For production use:
1. Add authentication & authorization
2. Implement database persistence
3. Add comprehensive error handling
4. Scale WebSocket infrastructure
5. Add audit logging

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- OpenAI GPT-4 for reasoning
- You.com for intelligence
- Composio for trading
- FastAPI & Next.js frameworks

---

## 📞 Contact

For questions or demo requests, see the demo guides:
- `DEMO_GUIDE.md` - Full 15-minute walkthrough
- `QUICK_DEMO.md` - 5-minute quick start
- `3_MINUTE_DEMO_SCRIPT.md` - Presentation script

---

**🛡️ Sovereign Sentinel - Detecting Shadow Defaults Before They Happen**
