"""
app.services.jobs.invoice_generator_service
"""

from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional, Tuple

import weasyprint
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base.secured_base_service import BaseSecuredService
from app.utils.constants import JINJA_TEMPLATES_PATH

templates = Jinja2Templates(directory=JINJA_TEMPLATES_PATH)


class InvoiceGeneratorService(BaseSecuredService):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)

    async def get_invoice_context(
        self,
        company_id: int,
        invoice_number: str,
        doc_type: str = "invoice",  # "invoice", "purchase", or "receipt"
    ) -> Dict[str, Any]:
        """
        Builds the full context required to render an invoice/purchase/receipt PDF.

        :param company_id: The company ID to fetch settings for
        :param data: The business data (items, customer, totals, etc.) – usually from order/invoice
        :param doc_type: One of "invoice", "purchase", "receipt"
        :return: Dict with data, settings, and selected template info
        """
        if doc_type not in ["invoice", "purchase", "receipt"]:
            raise ValueError("doc_type must be 'invoice', 'purchase', or 'receipt'")

        settings = None
        # await self.invoice_settings_repo.get_settings_data(
        #     session=self.session, company_id=company_id
        # )

        if not settings:
            raise ValueError(f"No invoice settings found for company_id={company_id}")

        # Determine which template code to use based on doc_type
        template_code = settings.get(f"{doc_type}_code")

        if not template_code:
            raise ValueError(
                f"No template code configured for {doc_type} in company settings"
            )

        template_ref = settings[f"{doc_type}_template"]

        # Helper to format dates nicely
        def format_date(
            date_str: Optional[str],
            format_in: str = "%Y/%m/%d",
            format_out: str = "%B %d, %Y",
        ) -> str:
            if not date_str:
                return ""
            try:
                dt = datetime.strptime(date_str, format_in)
                return dt.strftime(format_out)
            except ValueError:
                return date_str  # fallback

        # get report data from table using key fields
        invoices_model_data = None
        # await self.invoices_repo.get_first(
        #     session=self.session,
        #     filters={
        #         self.invoices_repo.model.company_id: company_id,
        #         self.invoices_repo.model.invoice_numb: invoice_number,
        #     },
        # )
        # data = invoices_model_data.indata.model_dump(exclude_none=True)
        data = {} #invoices_model_data.indata

        # Prepare formatted dates (common in templates)
        formatted_data = {} #data.copy()
        formatted_data["items"] = [
            item if isinstance(item, dict) else item.model_dump()
            for item in formatted_data["items"]
        ]

        formatted_data.setdefault("formatted_date", format_date(data.get("date")))
        formatted_data.setdefault(
            "formatted_due_date", format_date(data.get("due_date"))
        )
        formatted_data.setdefault(
            "formatted_delivery_date", format_date(data.get("delivery_date"))
        )

        # Build final context
        context = {
            "data": formatted_data,
            "settings": {
                "prefix_txt": settings.get("prefix_txt"),
                "due_days_numb": settings.get("due_days_numb"),
                "round_up_ind": settings.get("round_up_ind"),
                "show_company_details_ind": settings.get("show_company_details_ind"),
                "header_terms": settings.get("header_terms") or "",
                "footer_terms": settings.get("footer_terms") or "",
                "company_invoice_logo": settings.get("company_invoice_logo") or "",
            },
            "template": {
                "code": template_ref.get("code"),
                "description": template_ref.get("description"),
                "image_url": template_ref.get(
                    "image_url"
                ),  # e.g., background watermark or header image
                "type": template_ref.get(
                    "type"
                ),  # e.g., "INVOICE", "PURCHASE", "RECEIPT"
                "template_url": template_ref.get("template_url"),
                "sort_order": template_ref.get("sort_order"),
            },
            "doc_type": doc_type,
        }

        company_data = {
            "company_name": "Cow Dung Farm",
            "company_address": "456 Anyroad, Anywhere",
            "company_website": "interestingsite.com",
            "company_phone": "(123) 987-6543",
            "company_fax": "(123) 987-6542",
            "company_email": "happiest@example.com",
            "company_invoice_logo": "",
        }

        return {
            "context": context,
            "template_ref": template_ref,
            "company_data": company_data,
        }

    async def generate_pdf(
        self,
        company_id: int,
        invoice_number: str,
        doc_type: str,
        request_base_url: str | None = None,
    ) -> Tuple[bytes, str]:
        """
        Generate PDF for invoice, purchase order, or receipt.

        :param company_id: Company ID to fetch settings
        :param doc_type: "invoice", "purchase", or "receipt"
        :param data: Business data (invoice_number, date, items, customer, etc.)
        :param request_base_url: Base URL for WeasyPrint (e.g., str(request.base_url) in FastAPI)
        :return: (pdf_bytes, filename)
        """

        if doc_type not in ["invoice", "purchase", "receipt"]:
            raise ValueError("doc_type must be 'invoice', 'purchase', or 'receipt'")

        result = await self.get_invoice_context(company_id, invoice_number, doc_type)
        context = result["context"]
        template_ref = result["template_ref"]
        company_data = result["company_data"]

        # 6. Determine HTML template path
        template_path = context.get("template").get("template_url")
        # Example: invoice_templates/INV-01.html

        try:
            html_template = templates.get_template(template_path)
        except Exception as e:
            raise FileNotFoundError(f"Template file not found: {template_path}") from e

        # 7. Render HTML
        # html_content = html_template.render(**context)
        # Render HTML with full context including company_data
        html_content = html_template.render(
            data=context["data"],
            company_data=company_data,  # ← Explicitly passed
            settings=context["settings"],
            template=context["template"],
            doc_type=context["doc_type"],
            # Or just pass entire context if preferred:
            # **context
        )

        # 8. Generate PDF
        pdf_io = BytesIO()
        weasyprint.HTML(
            string=html_content, base_url=request_base_url or "http://localhost"
        ).write_pdf(pdf_io)
        pdf_io.seek(0)
        pdf_bytes = pdf_io.getvalue()

        # 9. Generate filename
        doc_name = doc_type.capitalize()
        invoice_num = context.get("data").get("invoice_number")
        filename = f"{doc_name}_{invoice_num}.pdf"

        return pdf_bytes, filename
