"""
Research Agent: Extrae datos financieros usando Composio MCP
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

try:
    from composio import ComposioToolset, Action, App
    from composio.client import ComposioClient
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Composio not available. Install with: pip install composio-core")

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Agent que extrae datos financieros de múltiples fuentes usando Composio."""
    
    def __init__(self, composio_api_key: str):
        """Initialize Research Agent with Composio client."""
        if not COMPOSIO_AVAILABLE:
            raise ImportError("Composio is not installed. Install with: pip install composio-core")
        self.client = ComposioClient(api_key=composio_api_key)
        self.toolset = ComposioToolset()
        
    async def extract_from_xero(
        self, 
        connection_id: str,
        tenant_id: str
    ) -> List[Dict]:
        """
        Extrae datos de préstamos desde Xero.
        
        Args:
            connection_id: ID de conexión OAuth de Xero
            tenant_id: ID del tenant de Xero
            
        Returns:
            Lista de transacciones/contratos convertidos a formato de préstamos
        """
        try:
            # Conectar con Xero usando Composio
            xero_app = App.XERO
            connection = self.client.get_connection(
                entity_id=connection_id,
                app=xero_app
            )
            
            # Extraer contactos (clientes) y facturas
            contacts = await self.toolset.execute_action(
                action=Action.XERO_GET_CONTACTS,
                connection=connection,
                params={"tenant_id": tenant_id}
            )
            
            # Extraer transacciones financieras
            transactions = await self.toolset.execute_action(
                action=Action.XERO_GET_TRANSACTIONS,
                connection=connection,
                params={"tenant_id": tenant_id}
            )
            
            # Convertir a formato LoanRecord
            loans = self._convert_xero_to_loans(contacts, transactions)
            logger.info(f"Extracted {len(loans)} loans from Xero")
            return loans
            
        except Exception as e:
            logger.error(f"Error extracting from Xero: {e}")
            raise
    
    async def extract_from_quickbooks(
        self,
        connection_id: str,
        company_id: str
    ) -> List[Dict]:
        """
        Extrae datos de préstamos desde QuickBooks.
        
        Args:
            connection_id: ID de conexión OAuth de QuickBooks
            company_id: ID de la compañía en QuickBooks
            
        Returns:
            Lista de préstamos en formato estandarizado
        """
        try:
            quickbooks_app = App.QUICKBOOKS
            connection = self.client.get_connection(
                entity_id=connection_id,
                app=quickbooks_app
            )
            
            # Extraer cuentas por cobrar (AR = préstamos)
            accounts_receivable = await self.toolset.execute_action(
                action=Action.QUICKBOOKS_GET_ACCOUNTS_RECEIVABLE,
                connection=connection,
                params={"company_id": company_id}
            )
            
            # Extraer transacciones de préstamos
            loans_data = await self.toolset.execute_action(
                action=Action.QUICKBOOKS_GET_LOANS,
                connection=connection,
                params={"company_id": company_id}
            )
            
            loans = self._convert_quickbooks_to_loans(accounts_receivable, loans_data)
            logger.info(f"Extracted {len(loans)} loans from QuickBooks")
            return loans
            
        except Exception as e:
            logger.error(f"Error extracting from QuickBooks: {e}")
            raise
    
    async def extract_from_stripe(
        self,
        connection_id: str
    ) -> List[Dict]:
        """
        Extrae datos de préstamos/financiamiento desde Stripe.
        
        Args:
            connection_id: ID de conexión de Stripe
            
        Returns:
            Lista de préstamos convertidos desde Stripe
        """
        try:
            stripe_app = App.STRIPE
            connection = self.client.get_connection(
                entity_id=connection_id,
                app=stripe_app
            )
            
            # Extraer balances y transacciones
            balance = await self.toolset.execute_action(
                action=Action.STRIPE_GET_BALANCE,
                connection=connection
            )
            
            # Extraer customer payment methods (pueden representar préstamos)
            customers = await self.toolset.execute_action(
                action=Action.STRIPE_GET_CUSTOMERS,
                connection=connection
            )
            
            loans = self._convert_stripe_to_loans(customers, balance)
            logger.info(f"Extracted {len(loans)} loans from Stripe")
            return loans
            
        except Exception as e:
            logger.error(f"Error extracting from Stripe: {e}")
            raise
    
    def _convert_xero_to_loans(self, contacts: List, transactions: List) -> List[Dict]:
        """Convierte datos de Xero a formato LoanRecord."""
        loans = []
        # Lógica de conversión específica para Xero
        # Mapear contactos y transacciones a préstamos
        for contact in contacts:
            # Buscar transacciones relacionadas
            related_transactions = [
                t for t in transactions 
                if t.get('contact_id') == contact.get('id')
            ]
            
            for trans in related_transactions:
                loan = {
                    'loanId': f"XERO_{contact.get('id')}_{trans.get('id')}",
                    'borrower': contact.get('name', 'Unknown'),
                    'industry': contact.get('industry', 'general'),
                    'interestType': self._infer_interest_type(trans),
                    'principalAmount': float(trans.get('total', 0)),
                    'outstandingBalance': float(trans.get('amount_due', 0)),
                    'maturityDate': self._parse_date(trans.get('due_date')),
                    'covenants': []
                }
                loans.append(loan)
        
        return loans
    
    def _convert_quickbooks_to_loans(self, ar_data: List, loans_data: List) -> List[Dict]:
        """Convierte datos de QuickBooks a formato LoanRecord."""
        loans = []
        # Lógica de conversión para QuickBooks
        for loan_item in loans_data:
            loan = {
                'loanId': f"QB_{loan_item.get('id')}",
                'borrower': loan_item.get('customer_name', 'Unknown'),
                'industry': loan_item.get('industry', 'general'),
                'interestType': loan_item.get('interest_type', 'Cash'),
                'principalAmount': float(loan_item.get('principal', 0)),
                'outstandingBalance': float(loan_item.get('balance', 0)),
                'maturityDate': self._parse_date(loan_item.get('maturity_date')),
                'covenants': loan_item.get('covenants', [])
            }
            loans.append(loan)
        
        return loans
    
    def _convert_stripe_to_loans(self, customers: List, balance: Dict) -> List[Dict]:
        """Convierte datos de Stripe a formato LoanRecord."""
        loans = []
        # Stripe generalmente no maneja préstamos directamente
        # Pero podemos mapear balances pendientes como préstamos
        for customer in customers:
            if customer.get('balance', 0) > 0:
                loan = {
                    'loanId': f"STRIPE_{customer.get('id')}",
                    'borrower': customer.get('name', customer.get('email', 'Unknown')),
                    'industry': 'general',
                    'interestType': 'Cash',
                    'principalAmount': float(customer.get('balance', 0)),
                    'outstandingBalance': float(customer.get('balance', 0)),
                    'maturityDate': datetime.now(),  # Stripe no tiene maturity dates
                    'covenants': []
                }
                loans.append(loan)
        
        return loans
    
    def _infer_interest_type(self, transaction: Dict) -> str:
        """Infiere el tipo de interés desde los datos de transacción."""
        # Lógica para determinar si es PIK, Cash o Hybrid
        description = transaction.get('description', '').lower()
        if 'pik' in description or 'payment-in-kind' in description:
            return 'PIK'
        elif 'hybrid' in description:
            return 'Hybrid'
        else:
            return 'Cash'
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parsea fecha desde string."""
        if not date_str:
            return datetime.now()
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now()
