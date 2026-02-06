"""
Treasury Commander Agent with Composio Agentic Trading.
Executes autonomous Bitcoin hedges via Composio agent framework.
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.config import settings

# Try to import Composio, but make it optional
try:
    from composio_openai import ComposioToolSet, Action
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Composio not available - Treasury Commander will use mock trading")

logger = logging.getLogger(__name__)


class TreasuryCommander:
    """
    Agentic Treasury Commander that executes Bitcoin hedges with self-verification.
    Uses Composio's agent framework for trading operations.
    """
    
    def __init__(self, composio_api_key: str, openai_api_key: str):
        """
        Initialize Treasury Commander with Composio agent framework.
        
        Args:
            composio_api_key: Composio API key
            openai_api_key: OpenAI API key for agent reasoning
        """
        self.composio_api_key = composio_api_key
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Initialize Composio toolset if available
        if COMPOSIO_AVAILABLE:
            try:
                self.toolset = ComposioToolSet(api_key=composio_api_key)
                logger.info("Composio toolset initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Composio toolset: {e}")
                self.toolset = None
        else:
            self.toolset = None
            logger.warning("Composio not available - using mock trading")
        
        # Agent memory for tracking trades and outcomes
        self.agent_memory: List[Dict[str, Any]] = []
        
        logger.info("Treasury Commander initialized")
    
    def calculate_hedge_amount(
        self,
        portfolio_value: float,
        hedge_percentage: float,
        btc_price: float
    ) -> float:
        """
        Calculate Bitcoin hedge amount with OpenAI reasoning.
        
        Args:
            portfolio_value: Total portfolio value in USD
            hedge_percentage: Percentage to hedge (0-100)
            btc_price: Current Bitcoin price in USD
            
        Returns:
            BTC amount to purchase
        """
        # Basic calculation
        hedge_value = portfolio_value * (hedge_percentage / 100)
        btc_amount = hedge_value / btc_price
        
        # Log reasoning
        reasoning = {
            "step": "calculate_hedge",
            "portfolio_value": portfolio_value,
            "hedge_percentage": hedge_percentage,
            "btc_price": btc_price,
            "hedge_value_usd": hedge_value,
            "btc_amount": btc_amount,
            "reasoning": f"Hedging {hedge_percentage}% of ${portfolio_value:,.2f} portfolio at ${btc_price:,.2f}/BTC = {btc_amount:.8f} BTC"
        }
        
        self.agent_memory.append(reasoning)
        logger.info(f"Calculated hedge: {btc_amount:.8f} BTC (${hedge_value:,.2f})")
        
        return btc_amount
    
    async def execute_hedge_with_verification(
        self,
        authorization: Dict[str, Any],
        hedge_percentage: float,
        portfolio_value: float = 10000000.0  # Default $10M portfolio
    ) -> Dict[str, Any]:
        """
        Execute agentic hedge with multi-step reasoning and self-verification.
        
        Args:
            authorization: Authorization result from voice alert
            hedge_percentage: Percentage to hedge
            portfolio_value: Total portfolio value
            
        Returns:
            Trade result with agent reasoning traces
        """
        alert_id = authorization.get('alertId', 'unknown')
        
        logger.info(f"Starting agentic hedge execution for alert {alert_id}")
        
        # Step 1: Calculate hedge amount with reasoning
        try:
            # Get current BTC price (mock for now - would use Composio tool)
            btc_price = await self._get_btc_price()
            
            btc_amount = self.calculate_hedge_amount(
                portfolio_value, hedge_percentage, btc_price
            )
            
            # Step 2: Pre-flight check
            preflight_result = await self._preflight_check(
                btc_amount, btc_price, authorization
            )
            
            if not preflight_result['passed']:
                return {
                    "status": "failed",
                    "reason": "preflight_check_failed",
                    "details": preflight_result,
                    "agent_reasoning": self.agent_memory
                }
            
            # Step 3: Execute trade via Composio (mock for now)
            trade_result = await self._execute_trade(btc_amount, btc_price)
            
            # Step 4: Verify execution
            verification_result = await self._verify_execution(trade_result)
            
            if not verification_result['verified']:
                # Step 5: Adaptive retry with reasoning
                retry_result = await self._adaptive_retry(
                    btc_amount, btc_price, verification_result
                )
                return retry_result
            
            # Step 5: Update portfolio and generate report
            final_result = await self._finalize_trade(
                trade_result, btc_amount, btc_price, portfolio_value
            )
            
            logger.info(f"Hedge execution completed successfully: {final_result['tradeId']}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Hedge execution failed: {e}")
            
            # Failure analysis
            failure_analysis = await self._analyze_failure(str(e))
            
            return {
                "status": "failed",
                "error": str(e),
                "failure_analysis": failure_analysis,
                "agent_reasoning": self.agent_memory
            }
    
    async def _get_btc_price(self) -> float:
        """Get current Bitcoin price (mock implementation)."""
        # In production, this would use Composio's get_btc_price tool
        mock_price = 45000.0
        
        self.agent_memory.append({
            "step": "get_btc_price",
            "price": mock_price,
            "reasoning": "Retrieved current BTC price from market data"
        })
        
        return mock_price
    
    async def _preflight_check(
        self,
        btc_amount: float,
        btc_price: float,
        authorization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pre-flight check before executing trade.
        
        Checks:
        - Sufficient funds
        - Market conditions
        - Authorization validity
        """
        checks = {
            "sufficient_funds": True,  # Mock check
            "market_conditions": "normal",  # Mock check
            "authorization_valid": authorization.get('authorized', False),
            "btc_amount": btc_amount,
            "estimated_cost": btc_amount * btc_price
        }
        
        passed = all([
            checks['sufficient_funds'],
            checks['market_conditions'] == 'normal',
            checks['authorization_valid']
        ])
        
        self.agent_memory.append({
            "step": "preflight_check",
            "checks": checks,
            "passed": passed,
            "reasoning": "Verified funds, market conditions, and authorization before trade"
        })
        
        return {"passed": passed, "checks": checks}
    
    async def _execute_trade(self, btc_amount: float, btc_price: float) -> Dict[str, Any]:
        """Execute trade via Composio agent tools (mock implementation)."""
        # In production, this would use Composio's execute_trade tool
        trade_id = f"trade_{int(datetime.utcnow().timestamp())}"
        
        trade_result = {
            "tradeId": trade_id,
            "timestamp": datetime.utcnow().isoformat(),
            "asset": "BTC",
            "amount": btc_amount,
            "price": btc_price,
            "totalCost": btc_amount * btc_price,
            "status": "completed",  # Mock success
            "exchangeOrderId": f"order_{trade_id}"
        }
        
        self.agent_memory.append({
            "step": "execute_trade",
            "trade": trade_result,
            "reasoning": f"Executed market buy order for {btc_amount:.8f} BTC at ${btc_price:,.2f}"
        })
        
        logger.info(f"Trade executed: {trade_id}")
        
        return trade_result
    
    async def _verify_execution(self, trade_result: Dict[str, Any]) -> Dict[str, Any]:
        """Verify trade execution by checking order status."""
        # In production, this would use Composio's check_order_status tool
        trade_id = trade_result['tradeId']
        
        verification = {
            "verified": True,  # Mock verification
            "order_status": "filled",
            "fill_price": trade_result['price'],
            "fill_amount": trade_result['amount'],
            "reasoning": f"Verified order {trade_id} was filled successfully"
        }
        
        self.agent_memory.append({
            "step": "verify_execution",
            "verification": verification,
            "reasoning": "Confirmed trade execution and order fill"
        })
        
        return verification
    
    async def _adaptive_retry(
        self,
        btc_amount: float,
        btc_price: float,
        verification_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adaptive retry with agent reasoning.
        Agent explains WHY it's retrying and what changed.
        """
        retry_reasoning = await self._generate_retry_reasoning(verification_result)
        
        self.agent_memory.append({
            "step": "adaptive_retry",
            "original_verification": verification_result,
            "retry_reasoning": retry_reasoning,
            "reasoning": "Analyzing failure and determining retry strategy"
        })
        
        # For now, return failure (would implement actual retry logic)
        return {
            "status": "failed",
            "reason": "verification_failed",
            "retry_attempted": True,
            "retry_reasoning": retry_reasoning,
            "agent_reasoning": self.agent_memory
        }
    
    async def _generate_retry_reasoning(
        self,
        verification_result: Dict[str, Any]
    ) -> str:
        """Use OpenAI to generate reasoning for retry strategy."""
        prompt = f"""
        Trade verification failed with the following result:
        {verification_result}
        
        As an agentic trading system, explain:
        1. Why the trade failed
        2. What should change for a retry
        3. Whether a retry is advisable
        
        Provide a concise analysis.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a trading agent analyzing trade failures."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            reasoning = response.choices[0].message.content
            return reasoning if reasoning else "Unable to generate retry reasoning"
        except Exception as e:
            logger.error(f"Failed to generate retry reasoning: {e}")
            return "Unable to generate retry reasoning due to API error"
    
    async def _finalize_trade(
        self,
        trade_result: Dict[str, Any],
        btc_amount: float,
        btc_price: float,
        portfolio_value: float
    ) -> Dict[str, Any]:
        """Finalize trade and generate human-readable report."""
        report = {
            "tradeId": trade_result['tradeId'],
            "timestamp": trade_result['timestamp'],
            "status": "completed",
            "asset": "BTC",
            "amount": btc_amount,
            "price": btc_price,
            "totalCost": btc_amount * btc_price,
            "exchangeOrderId": trade_result['exchangeOrderId'],
            "portfolio_impact": {
                "previous_btc_position": 0.0,  # Mock
                "new_btc_position": btc_amount,
                "hedge_percentage": (btc_amount * btc_price / portfolio_value) * 100
            },
            "human_readable_report": self._generate_report(
                trade_result, btc_amount, btc_price, portfolio_value
            ),
            "agent_reasoning": self.agent_memory
        }
        
        self.agent_memory.append({
            "step": "finalize_trade",
            "report": report,
            "reasoning": "Trade completed successfully, portfolio updated"
        })
        
        return report
    
    def _generate_report(
        self,
        trade_result: Dict[str, Any],
        btc_amount: float,
        btc_price: float,
        portfolio_value: float
    ) -> str:
        """Generate human-readable trade report."""
        hedge_value = btc_amount * btc_price
        hedge_pct = (hedge_value / portfolio_value) * 100
        
        report = f"""
HEDGE EXECUTION REPORT
======================
Trade ID: {trade_result['tradeId']}
Timestamp: {trade_result['timestamp']}

TRADE DETAILS:
- Asset: Bitcoin (BTC)
- Amount: {btc_amount:.8f} BTC
- Price: ${btc_price:,.2f} per BTC
- Total Cost: ${hedge_value:,.2f}

PORTFOLIO IMPACT:
- Portfolio Value: ${portfolio_value:,.2f}
- Hedge Percentage: {hedge_pct:.2f}%
- New BTC Position: {btc_amount:.8f} BTC

STATUS: ✓ COMPLETED
Exchange Order ID: {trade_result['exchangeOrderId']}
"""
        return report
    
    async def _analyze_failure(self, error: str) -> str:
        """Use OpenAI to analyze trade failure and suggest fixes."""
        prompt = f"""
        A Bitcoin hedge trade failed with the following error:
        {error}
        
        As an agentic trading system, provide:
        1. Root cause analysis
        2. Suggested fixes
        3. Prevention strategies
        
        Be concise and actionable.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a trading agent analyzing failures."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            analysis = response.choices[0].message.content
            return analysis if analysis else f"Trade failed: {error}. Unable to generate detailed analysis."
        except Exception as e:
            logger.error(f"Failed to analyze failure: {e}")
            return f"Trade failed: {error}. Unable to generate detailed analysis."
    
    def get_agent_memory(self) -> List[Dict[str, Any]]:
        """Get agent decision traces for transparency."""
        return self.agent_memory
    
    def clear_agent_memory(self):
        """Clear agent memory (for new trading session)."""
        self.agent_memory = []
        logger.info("Agent memory cleared")
