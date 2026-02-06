"""
Company Analyzer: Deep financial analysis of custom companies with industry-specific risk assessment.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.openai_client import OpenAIClient
from app.you_client import YouAPIClient

logger = logging.getLogger(__name__)


class CompanyAnalyzer:
    """Analyzes custom company financial data and assesses risk."""
    
    def __init__(self, openai_api_key: str, you_api_key: str):
        """Initialize company analyzer."""
        self.openai_client = OpenAIClient(api_key=openai_api_key)
        self.you_client = YouAPIClient(api_key=you_api_key)
    
    async def analyze_company(
        self,
        company_name: str,
        industry: str,
        financial_data: Dict[str, Any],
        analysis_focus: List[str]
    ) -> Dict[str, Any]:
        """
        Comprehensive company risk analysis.
        
        Args:
            company_name: Name of the company
            industry: Industry sector
            financial_data: Dict with income_statement, balance_sheet, cash_flow
            analysis_focus: List of risk areas to focus on (e.g., ["liquidity", "profitability", "solvency"])
        
        Returns:
            Comprehensive risk assessment
        """
        logger.info(f"Analyzing {company_name} in {industry} industry")
        
        # Step 1: Industry research
        industry_intel = await self._research_industry(industry)
        
        # Step 2: Financial ratio analysis
        ratios = self._calculate_financial_ratios(financial_data)
        
        # Step 3: AI-powered risk assessment
        risk_assessment = await self._assess_risks(
            company_name, industry, financial_data, ratios, industry_intel, analysis_focus
        )
        
        # Step 4: Generate recommendations
        recommendations = await self._generate_recommendations(
            company_name, risk_assessment, ratios
        )
        
        return {
            "company": company_name,
            "industry": industry,
            "timestamp": datetime.utcnow().isoformat(),
            "financial_ratios": ratios,
            "industry_intelligence": industry_intel,
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
            "overall_risk_score": risk_assessment.get("overall_score", 50)
        }
    
    async def _research_industry(self, industry: str) -> Dict[str, Any]:
        """Research industry trends and risks using You.com."""
        try:
            query = f"{industry} industry trends risks challenges 2025"
            
            search_results = await self.you_client.search(
                query=query,
                num_results=10
            )
            
            # Extract key insights
            articles = []
            for hit in search_results.get('hits', [])[:5]:
                articles.append({
                    "title": hit.get('title', ''),
                    "snippet": hit.get('snippets', [''])[0] if hit.get('snippets') else '',
                    "url": hit.get('url', '')
                })
            
            # Use AI to summarize industry risks
            summary_prompt = f"""Analyze these articles about the {industry} industry and identify:
1. Top 3 industry risks
2. Market trends
3. Competitive pressures
4. Regulatory concerns

Articles:
{chr(10).join([f"- {a['title']}: {a['snippet']}" for a in articles])}

Provide a concise summary."""
            
            summary = self.openai_client.analyze_with_reasoning(
                system_prompt="You are a financial industry analyst.",
                user_prompt=summary_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            return {
                "industry": industry,
                "top_risks": summary,
                "articles": articles,
                "search_query": query
            }
            
        except Exception as e:
            logger.error(f"Industry research failed: {e}")
            return {
                "industry": industry,
                "top_risks": "Industry research unavailable",
                "articles": [],
                "error": str(e)
            }
    
    def _calculate_financial_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key financial ratios including 6 priority credit metrics."""
        try:
            # Extract data
            income = financial_data.get('income_statement', {})
            balance = financial_data.get('balance_sheet', {})
            cashflow = financial_data.get('cash_flow', {})
            
            # Current year data
            revenue = income.get('total_revenue', 0)
            net_income = income.get('net_income', 0)
            operating_income = income.get('operating_income', 0)
            ebitda = income.get('ebitda', operating_income + income.get('depreciation', 0))
            interest_expense = abs(income.get('interest_expense', 0))
            
            current_assets = balance.get('total_current_assets', 0)
            current_liabilities = balance.get('total_current_liabilities', 0)
            total_assets = balance.get('total_assets', 0)
            total_liabilities = balance.get('total_liabilities', 0)
            total_equity = balance.get('total_equity', 0)
            retained_earnings = balance.get('retained_earnings', 0)
            working_capital = current_assets - current_liabilities
            
            operating_cash_flow = cashflow.get('net_cash_from_operating', 0)
            
            # Debt service (principal + interest)
            annual_principal = income.get('principal_payments', total_liabilities * 0.1)  # Estimate 10% annual
            total_debt_service = annual_principal + interest_expense
            
            # === 6 PRIORITY CREDIT METRICS ===
            
            # 1. Debt Service Coverage Ratio (DSCR)
            dscr = (ebitda / total_debt_service) if total_debt_service > 0 else 0
            dscr_score = (
                100 if dscr >= 1.50 else
                80 if dscr >= 1.25 else
                50 if dscr >= 1.00 else
                20 if dscr >= 0.80 else 0
            )
            
            # 2. Debt-to-Equity Ratio
            debt_to_equity = (total_liabilities / total_equity) if total_equity > 0 else 999
            de_score = (
                100 if debt_to_equity < 1.0 else
                80 if debt_to_equity < 1.5 else
                50 if debt_to_equity < 2.5 else
                20 if debt_to_equity < 4.0 else 0
            )
            
            # 3. Current Ratio
            current_ratio = (current_assets / current_liabilities) if current_liabilities > 0 else 0
            cr_score = (
                100 if current_ratio >= 2.0 else
                80 if current_ratio >= 1.5 else
                50 if current_ratio >= 1.2 else
                20 if current_ratio >= 1.0 else 0
            )
            
            # 4. Interest Coverage Ratio (ICR)
            icr = (ebitda / interest_expense) if interest_expense > 0 else 999
            icr_score = (
                100 if icr >= 5.0 else
                80 if icr >= 3.0 else
                50 if icr >= 2.0 else
                20 if icr >= 1.5 else 0
            )
            
            # 5. Net Profit Margin
            net_margin = (net_income / revenue * 100) if revenue > 0 else 0
            npm_score = (
                100 if net_margin >= 15 else
                80 if net_margin >= 10 else
                50 if net_margin >= 5 else
                20 if net_margin >= 0 else 0
            )
            
            # 6. Altman Z'-Score (Private Companies)
            # Z' = 0.717X1 + 0.847X2 + 3.107X3 + 0.420X4 + 0.998X5
            x1 = working_capital / total_assets if total_assets > 0 else 0
            x2 = retained_earnings / total_assets if total_assets > 0 else 0
            x3 = ebitda / total_assets if total_assets > 0 else 0
            x4 = total_equity / total_liabilities if total_liabilities > 0 else 0
            x5 = revenue / total_assets if total_assets > 0 else 0
            
            z_score = (0.717 * x1) + (0.847 * x2) + (3.107 * x3) + (0.420 * x4) + (0.998 * x5)
            z_score_interpretation = (
                "Safe Zone" if z_score > 2.9 else
                "Grey Zone" if z_score > 1.23 else
                "Distress Zone"
            )
            z_score_score = (
                100 if z_score > 2.9 else
                60 if z_score > 1.23 else 20
            )
            
            # Overall Credit Score (weighted average of 6 metrics)
            overall_credit_score = (
                dscr_score * 0.25 +
                de_score * 0.20 +
                cr_score * 0.15 +
                icr_score * 0.15 +
                npm_score * 0.10 +
                z_score_score * 0.15
            )
            
            ratios = {
                # === 6 PRIORITY METRICS ===
                "dscr": round(dscr, 2),
                "dscr_score": dscr_score,
                "debt_to_equity": round(debt_to_equity, 2),
                "de_score": de_score,
                "current_ratio": round(current_ratio, 2),
                "cr_score": cr_score,
                "interest_coverage_ratio": round(icr, 2),
                "icr_score": icr_score,
                "net_profit_margin": round(net_margin, 1),
                "npm_score": npm_score,
                "altman_z_score": round(z_score, 2),
                "z_score_interpretation": z_score_interpretation,
                "z_score_score": z_score_score,
                "overall_credit_score": round(overall_credit_score, 1),
                
                # Additional ratios
                "operating_margin": (operating_income / revenue * 100) if revenue else 0,
                "return_on_assets": (net_income / total_assets * 100) if total_assets else 0,
                "return_on_equity": (net_income / total_equity * 100) if total_equity else 0,
                "quick_ratio": ((current_assets - balance.get('inventory', 0)) / current_liabilities) if current_liabilities else 0,
                "debt_to_assets": (total_liabilities / total_assets) if total_assets else 0,
                "operating_cash_flow_ratio": (operating_cash_flow / current_liabilities) if current_liabilities else 0,
                "cash_flow_to_debt": (operating_cash_flow / total_liabilities) if total_liabilities else 0
            }
            
            return ratios
            
        except Exception as e:
            logger.error(f"Ratio calculation failed: {e}")
            return {}
    
    async def _assess_risks(
        self,
        company_name: str,
        industry: str,
        financial_data: Dict[str, Any],
        ratios: Dict[str, Any],
        industry_intel: Dict[str, Any],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """AI-powered comprehensive risk assessment."""
        
        # Build analysis prompt
        prompt = f"""Analyze the financial health and risk profile of {company_name}, a {industry} company.

FINANCIAL RATIOS:
- Net Profit Margin: {ratios.get('net_profit_margin', 0):.1f}%
- Operating Margin: {ratios.get('operating_margin', 0):.1f}%
- Current Ratio: {ratios.get('current_ratio', 0):.2f}
- Debt-to-Equity: {ratios.get('debt_to_equity', 0):.2f}
- Return on Equity: {ratios.get('return_on_equity', 0):.1f}%
- Operating Cash Flow Ratio: {ratios.get('operating_cash_flow_ratio', 0):.2f}

INDUSTRY CONTEXT:
{industry_intel.get('top_risks', 'No industry data')}

FOCUS AREAS: {', '.join(focus_areas)}

Provide a comprehensive risk assessment covering:
1. Overall Risk Score (0-100, where 100 is highest risk)
2. Liquidity Risk (ability to meet short-term obligations)
3. Profitability Risk (sustainability of earnings)
4. Solvency Risk (long-term debt burden)
5. Industry-Specific Risks
6. Red Flags (critical issues)
7. Strengths (positive indicators)

Format:
OVERALL_SCORE: <number>
LIQUIDITY_RISK: <low/medium/high> - <explanation>
PROFITABILITY_RISK: <low/medium/high> - <explanation>
SOLVENCY_RISK: <low/medium/high> - <explanation>
INDUSTRY_RISK: <low/medium/high> - <explanation>
RED_FLAGS: <list>
STRENGTHS: <list>"""
        
        try:
            response = self.openai_client.analyze_with_reasoning(
                system_prompt="You are a senior credit analyst at a major bank. Provide detailed, actionable risk assessments.",
                user_prompt=prompt,
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse response
            assessment = {
                "overall_score": 50,
                "liquidity_risk": "medium",
                "profitability_risk": "medium",
                "solvency_risk": "medium",
                "industry_risk": "medium",
                "red_flags": [],
                "strengths": [],
                "detailed_analysis": response
            }
            
            # Extract score
            if "OVERALL_SCORE:" in response:
                try:
                    score_str = response.split("OVERALL_SCORE:")[1].split("\n")[0].strip()
                    assessment["overall_score"] = float(score_str)
                except:
                    pass
            
            # Extract risk levels
            for risk_type in ["LIQUIDITY_RISK", "PROFITABILITY_RISK", "SOLVENCY_RISK", "INDUSTRY_RISK"]:
                if risk_type in response:
                    risk_line = response.split(risk_type + ":")[1].split("\n")[0].strip()
                    if "low" in risk_line.lower():
                        assessment[risk_type.lower()] = "low"
                    elif "high" in risk_line.lower():
                        assessment[risk_type.lower()] = "high"
                    else:
                        assessment[risk_type.lower()] = "medium"
            
            # Extract red flags
            if "RED_FLAGS:" in response:
                flags_section = response.split("RED_FLAGS:")[1].split("STRENGTHS:")[0] if "STRENGTHS:" in response else response.split("RED_FLAGS:")[1]
                assessment["red_flags"] = [line.strip("- ").strip() for line in flags_section.split("\n") if line.strip().startswith("-")]
            
            # Extract strengths
            if "STRENGTHS:" in response:
                strengths_section = response.split("STRENGTHS:")[1]
                assessment["strengths"] = [line.strip("- ").strip() for line in strengths_section.split("\n") if line.strip().startswith("-")]
            
            return assessment
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {
                "overall_score": 50,
                "error": str(e),
                "detailed_analysis": "Risk assessment unavailable"
            }
    
    async def _generate_recommendations(
        self,
        company_name: str,
        risk_assessment: Dict[str, Any],
        ratios: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations."""
        
        prompt = f"""Based on this risk assessment for {company_name}, provide 5 specific, actionable recommendations for a bank considering lending to this company.

Risk Score: {risk_assessment.get('overall_score', 50)}/100
Red Flags: {', '.join(risk_assessment.get('red_flags', ['None']))}
Current Ratio: {ratios.get('current_ratio', 0):.2f}
Debt-to-Equity: {ratios.get('debt_to_equity', 0):.2f}

Provide recommendations in this format:
1. <recommendation>
2. <recommendation>
etc."""
        
        try:
            response = self.openai_client.analyze_with_reasoning(
                system_prompt="You are a senior credit officer providing lending recommendations.",
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse recommendations
            recommendations = []
            for line in response.split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-")):
                    rec = line.lstrip("0123456789.-) ").strip()
                    if rec:
                        recommendations.append(rec)
            
            return recommendations[:5]
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Unable to generate recommendations"]
