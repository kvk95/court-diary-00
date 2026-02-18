"""
Docstring for app.services.jobs.pdf_report_service
"""

from datetime import datetime
from io import BytesIO
from typing import Tuple

import httpx
import weasyprint
from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base.secured_base_service import BaseSecuredService
from app.validators.error_codes import ErrorCodes
from app.validators.validation_errors import ValidationErrorDetail
from app.utils.constants import JINJA_TEMPLATES_PATH

templates = Jinja2Templates(directory=JINJA_TEMPLATES_PATH)


class PdfReportService(BaseSecuredService):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)

    async def generate_pdf(
        self,
        request: Request,
    ) -> Tuple[bytes, str]:

        # Parse request body
        body = await request.json()
        target_path = body.get(
            "target_path"
        )  # "reports/invoice/paged?page=1&limit=12&from_date=2026-01-06&to_date=2026-01-12"
        target_method = body.get("target_method", "GET")
        columns = body.get("columns", [])  # List of column configs
        title = body.get("title", "NO NAME")
        filename = body.get("filename", "TEST")

        if not target_path:
            raise ValidationErrorDetail(
                code=ErrorCodes.VALIDATION_ERROR,
                message="target_path is required",
            )

        # Forward original headers if needed (be careful with auth headers)
        headers = dict(request.headers)

        # Remove Host header to avoid conflicts
        headers.pop("host", None)

        # Build the full URL (adjust base URL as needed)
        base_url = str(request.base_url).rstrip("/")
        target_url = f"{base_url}/api/{target_path}"

        # Use async HTTP client to call the target endpoint
        async with httpx.AsyncClient() as client:
            try:
                # Forward the original method and body
                method = request.method
                body = await request.body()

                response = await client.request(
                    method=target_method,
                    url=target_url,
                    headers=headers,
                    content=body if body else None,
                    params=dict(request.query_params),
                )

                response.raise_for_status()

                json_data = response.json()
                data = json_data["result"]["records"]
                total_records = json_data["result"]["paging"]["total_records"]

            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # 2. Format data according to column config
        formatted_data = []
        for row in data:
            formatted_row = {}
            for col in columns:
                value = row.get(col["key"])
                if value is not None and col.get("format"):
                    if col["format"] == "currency":
                        value = f"₹ {float(value):,.2f}"
                    elif col["format"] == "date" and value:
                        value = datetime.fromisoformat(value).strftime("%d/%m/%Y")
                    elif col["format"] == "status":
                        value = value.upper()  # or your badge logic
                formatted_row[col["key"]] = str(value) if value is not None else ""
            formatted_data.append(formatted_row)

        template_path = "templates/pdf_report.html"
        try:
            html_template = templates.get_template(template_path)
        except Exception as e:
            raise FileNotFoundError(f"Template file not found: {template_path}") from e

        company_settings = {} 
        # await self.company_settings_repo.get_by_id(
        #     session=self.session, id_values=self.company_id
        # )

        html_content = html_template.render(
            title=title,  # "Invoice Report"
            data=formatted_data,  # Your table data
            total_records=25,
            columns=columns,
            generated_date=datetime.now().strftime("%d %b %Y %I:%M %p"),
            # company_name=f"{company_settings.company_name} | {company_settings.phone}",
        )

        # 8. Generate PDF
        pdf_io = BytesIO()
        weasyprint.HTML(
            string=html_content, base_url=str(request.base_url) or "http://localhost"
        ).write_pdf(pdf_io)
        pdf_io.seek(0)

        return pdf_io, filename
