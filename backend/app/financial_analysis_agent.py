"""
Financial Analysis Agent: Analiza datos financieros usando modelo open source
"""
import logging
import json
import re
from typing import List, Dict, Optional
from datetime import datetime

try:
    from langchain_community.llms import Ollama
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("LangChain not available. Install with: pip install langchain langchain-community")

from app.models import LoanRecord, FlaggedLoan

logger = logging.getLogger(__name__)


class FinancialAnalysisAgent:
    """
    Agent que analiza datos financieros usando modelo open source local.
    Usa Ollama con LLaMA 2 o Mistral para análisis.
    """
    
    def __init__(self, model_name: str = "llama2", base_url: str = "http://localhost:11434"):
        """
        Initialize Financial Analysis Agent.
        
        Args:
            model_name: Nombre del modelo en Ollama (llama2, mistral, etc.)
            base_url: URL del servidor Ollama
        """
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, will use fallback analysis only")
            self.llm = None
            self.chain = None
            return
            
        try:
            self.llm = Ollama(model=model_name, base_url=base_url)
            self.analysis_prompt = PromptTemplate(
                input_variables=["loan_data", "risk_context"],
                template="""
                Eres un analista financiero experto. Analiza el siguiente préstamo y determina:
                
                Datos del préstamo:
                {loan_data}
                
                Contexto de riesgo:
                {risk_context}
                
                Responde en formato JSON con:
                {{
                    "risk_level": "low|medium|high|critical",
                    "risk_factors": ["factor1", "factor2"],
                    "recommendation": "recomendación breve",
                    "is_pik_risk": true/false,
                    "shadow_default_probability": 0.0-1.0
                }}
                """
            )
            self.chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
            logger.info(f"Financial Analysis Agent initialized with model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama, will use fallback analysis: {e}")
            self.llm = None
            self.chain = None
    
    async def analyze_loan(
        self,
        loan: LoanRecord,
        risk_context: Dict
    ) -> Dict:
        """
        Analiza un préstamo individual usando el modelo.
        
        Args:
            loan: Registro de préstamo a analizar
            risk_context: Contexto de riesgo geopolítico actual
            
        Returns:
            Diccionario con análisis del préstamo
        """
        try:
            if self.chain is None:
                return self._fallback_analysis(loan, risk_context)
            
            loan_data = loan.model_dump_json()
            
            # Preparar contexto de riesgo
            context_str = f"""
            Global Risk Score: {risk_context.get('global_risk_score', 0)}
            Affected Sectors: {', '.join(risk_context.get('affected_sectors', []))}
            Sentiment: {risk_context.get('sentiment', 'neutral')}
            """
            
            # Ejecutar análisis con LLM
            result = await self.chain.ainvoke({
                "loan_data": loan_data,
                "risk_context": context_str
            })
            
            # Parsear respuesta JSON del modelo
            analysis = self._parse_llm_response(result['text'])
            
            logger.info(f"Analyzed loan {loan.loan_id}: {analysis.get('risk_level')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing loan {loan.loan_id}: {e}")
            # Fallback a análisis básico
            return self._fallback_analysis(loan, risk_context)
    
    async def analyze_portfolio(
        self,
        loans: List[LoanRecord],
        risk_context: Dict
    ) -> List[FlaggedLoan]:
        """
        Analiza un portafolio completo de préstamos.
        
        Args:
            loans: Lista de préstamos a analizar
            risk_context: Contexto de riesgo geopolítico
            
        Returns:
            Lista de préstamos marcados como de alto riesgo
        """
        flagged_loans = []
        
        for loan in loans:
            analysis = await self.analyze_loan(loan, risk_context)
            
            # Si el modelo indica riesgo alto o crítico, marcar el préstamo
            if analysis.get('risk_level') in ['high', 'critical']:
                flagged_loan = FlaggedLoan(
                    **loan.model_dump(),
                    flag_reason=analysis.get('recommendation', 'High risk detected by AI analysis'),
                    risk_level=analysis.get('risk_level', 'medium'),
                    correlated_event=risk_context.get('correlated_event', 'Geopolitical risk'),
                    flagged_at=datetime.utcnow()
                )
                flagged_loans.append(flagged_loan)
        
        logger.info(f"Flagged {len(flagged_loans)} loans out of {len(loans)}")
        return flagged_loans
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parsea la respuesta JSON del LLM."""
        # Extraer JSON de la respuesta (puede tener texto adicional)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # Fallback si no se puede parsear
        return {
            "risk_level": "medium",
            "risk_factors": ["Unable to parse AI response"],
            "recommendation": "Manual review required",
            "is_pik_risk": False,
            "shadow_default_probability": 0.5
        }
    
    def _fallback_analysis(self, loan: LoanRecord, risk_context: Dict) -> Dict:
        """Análisis básico de fallback si el LLM falla."""
        risk_level = "low"
        risk_factors = []
        
        if loan.interest_type == 'PIK':
            risk_level = "high"
            risk_factors.append("PIK interest type")
        
        if loan.outstanding_balance > 10_000_000:
            risk_level = "critical" if risk_level == "high" else "high"
            risk_factors.append("High outstanding balance")
        
        if risk_context.get('global_risk_score', 0) > 70:
            risk_level = "high" if risk_level == "low" else risk_level
            risk_factors.append("High global risk score")
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": f"PIK loan with {loan.outstanding_balance} outstanding",
            "is_pik_risk": loan.interest_type == 'PIK',
            "shadow_default_probability": 0.3 if risk_level == "high" else 0.1
        }
