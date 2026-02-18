from app.dtos.base.base_data import BaseRecordData, BaseInData
from typing import Dict, Optional

class InvoiceReceiptEmailDto(BaseInData):
    """
    All data needed to render and send invoice receipt email.
    FinanceService prepares this DTO, EmailService consumes it.
    """
    invoice_id: str
    recipient_email: str
    subject_template: Optional[str] = None   
    content_template: Optional[str] = None       
    
    # Template replacement tags/values (FinanceService fills these)
    tags: Dict[str, str] = {}                     
    
    # PDF attachment (passed as bytes)
    pdf_bytes: bytes
    pdf_filename: str                             

    # Optional overrides / extras
    company_id: int = 1001
    from_email: Optional[str] = None         


class SendEmailStatusDto(BaseRecordData):
    status: str
    sent_to: str
    subject: str
    invoice_id: str