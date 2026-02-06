# Composio Integration Setup Guide

## Overview

Sovereign Sentinel uses Composio to connect with financial services (Xero, QuickBooks, Stripe) and extract loan data automatically.

## Step 1: Get Composio API Key

1. Sign up at [https://platform.composio.dev](https://platform.composio.dev)
2. Navigate to your workspace
3. Go to **Settings** → **API Keys**
4. Create a new API key or copy an existing one
5. Add it to your `.env` file:

```bash
COMPOSIO_API_KEY=your_composio_api_key_here
```

## Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install `composio-core>=0.3.0`.

## Step 3: Create MCP Server in Composio Dashboard

1. Go to [https://platform.composio.dev](https://platform.composio.dev)
2. Navigate to your project
3. Go to **MCP Configs** section
4. Click **"+ Create new MCP server"**
5. Enter an **External User ID** (unique identifier for your system, e.g., `user-123` or `pg-test-fbbef01e-671d-4816-bac1-0546cea96299`)
6. Click **"Connect Account"** for each app you want to use:
   - **Xero**: Connect your Xero account
   - **QuickBooks**: Connect your QuickBooks account
   - **Stripe**: Connect your Stripe account
7. Click **"Create Server"**

After connecting, you'll get connection IDs for each app (e.g., `mcp_xero-xtw5so`, `mcp_stripe-jzfimt`).

## Step 4: Use the API

### Option A: Create Connection via API

```bash
POST /api/composio/connect
{
  "app": "xero",
  "entity_id": "your-external-user-id",
  "redirect_url": "https://your-app.com/callback"  # Optional
}
```

Response:
```json
{
  "connection_id": "conn_123",
  "auth_url": "https://...",
  "status": "pending"
}
```

### Option B: List Existing Connections

```bash
GET /api/composio/connections?entity_id=your-external-user-id
```

Response:
```json
{
  "connections": [
    {
      "id": "mcp_xero-xtw5so",
      "app": "xero",
      "status": "connected",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

### Option C: Extract Data Using Connection

```bash
POST /api/research/extract
{
  "source": "xero",
  "connection_id": "mcp_xero-xtw5so",
  "tenant_id": "your-xero-tenant-id"
}
```

## Step 5: Extract and Analyze

Once you have connections set up, you can extract and analyze loan data:

```bash
POST /api/research/analyze-and-extract
{
  "source": "xero",
  "connection_id": "mcp_xero-xtw5so",
  "tenant_id": "your-tenant-id",
  "use_ai": true
}
```

## Important Notes

1. **External User ID**: This is a unique identifier in YOUR system. Use the same ID consistently for the same user/organization.

2. **Connection IDs**: After connecting accounts in Composio dashboard, you'll see connection IDs like `mcp_xero-xtw5so`. Use these in API calls.

3. **Tenant ID**: Required for Xero and QuickBooks:
   - **Xero**: Found in Xero dashboard → Settings → General Settings → Organization ID
   - **QuickBooks**: Found in QuickBooks dashboard → Company Settings → Company ID

4. **Stripe**: No tenant ID needed, just the connection ID.

## Troubleshooting

### Error: "Research Agent not initialized"
- Verify `COMPOSIO_API_KEY` is in `.env` file
- Restart the server after adding the key

### Error: "Composio is not installed"
```bash
pip install composio-core
```

### Error: "Connection not found"
- Verify the connection ID exists in Composio dashboard
- Check that the connection status is "connected"
- Ensure you're using the correct entity_id

### Error: "Invalid app name"
- Use lowercase: "xero", "quickbooks", or "stripe"
- Check spelling

## Example Workflow

1. **Create connection** (via Composio dashboard or API)
2. **Get connection ID** from dashboard or API response
3. **Extract data** using connection ID
4. **Analyze portfolio** with extracted loans
5. **Review flagged loans** for high-risk PIK loans

## API Endpoints Summary

- `GET /api/composio/connections` - List all connections
- `POST /api/composio/connect` - Create new connection
- `POST /api/research/extract` - Extract data from connected app
- `POST /api/research/analyze-and-extract` - Extract and analyze in one step
- `POST /api/analysis/analyze` - Analyze loan portfolio
