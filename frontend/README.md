# Sovereign Sentinel - War Room Dashboard

## Overview

The War Room Dashboard is a real-time monitoring interface for the Sovereign Sentinel system. It provides visibility into geopolitical risk scores, flagged loans, alerts, agent activity, and policy configuration.

## Features

### Components

1. **RiskGauge** - Circular gauge displaying the current Global Risk Score (0-100) with color-coded severity levels
2. **LoanTable** - Interactive table of flagged loans with PIK status toggle functionality
3. **AlertPanel** - Prominent display of critical alerts and warnings
4. **AgentChatLog** - Live feed of agent activity showing reasoning and outcomes
5. **PolicyOverridePanel** - Interface for viewing and editing policy configuration

### Real-time Updates

The dashboard uses WebSocket connections to receive live updates:
- Risk score changes
- New agent activity logs
- Alert notifications
- Loan status updates
- Policy configuration changes

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000)

## Architecture

### Frontend Stack
- Next.js 14 (App Router)
- React 18
- TypeScript
- TailwindCSS

### API Integration
- REST API for data fetching and mutations
- WebSocket for real-time updates
- Automatic reconnection with exponential backoff

### File Structure
```
frontend/
├── app/
│   ├── page.tsx          # Main dashboard page
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── components/
│   ├── RiskGauge.tsx
│   ├── LoanTable.tsx
│   ├── AlertPanel.tsx
│   ├── AgentChatLog.tsx
│   └── PolicyOverridePanel.tsx
├── lib/
│   ├── api.ts            # REST API client
│   └── websocket.ts      # WebSocket client
└── types/
    └── index.ts          # TypeScript type definitions
```

## Usage

### Monitoring Risk
The RiskGauge component displays the current risk score with color coding:
- Green (0-49): Normal
- Yellow (50-69): Elevated
- Orange (70-79): High
- Red (80-100): Critical

### Managing Loans
Click on a loan's PIK status button to toggle between PIK and Cash payment types. Changes are immediately persisted and broadcast to all connected clients.

### Policy Overrides
Click "Edit Policy" to modify risk thresholds, exposure limits, or hedge percentages. All changes require a reason and are logged for audit purposes.

### Agent Activity
The agent log shows real-time activity from all agents (OSINT Scout, Forensic Auditor, Policy Brain, Treasury Commander) with their reasoning and outcomes.

## API Endpoints

The dashboard communicates with these backend endpoints:

- `GET /api/dashboard/state` - Complete dashboard state
- `GET /api/risk/current` - Current risk score
- `GET /api/loans/flagged` - Flagged loans list
- `POST /api/loans/{id}/pik-status` - Toggle PIK status
- `GET /api/policy/config` - Policy configuration
- `POST /api/policy/override` - Apply policy override
- `GET /api/logs/agents` - Agent activity logs
- `GET /api/system/status` - System status
- `WS /ws` - WebSocket connection for real-time updates

## Development

### Building for Production
```bash
npm run build
npm start
```

### Linting
```bash
npm run lint
```

## Notes

- The dashboard is designed for desktop viewing but includes responsive design
- WebSocket connections automatically reconnect on disconnection
- All timestamps are displayed in local timezone
- Currency values are formatted in USD
