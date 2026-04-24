# app/whatsapp/webhook.py

from fastapi import HTTPException,  Depends, Request
from fastapi.responses import PlainTextResponse

from app.api.v1.routes.base.base_controller import BaseController
from app.services.calendar_service import CalendarService
from app.services.cases_service import CasesService
from app.whatsapp.handler import handle_message
from app.dependencies import get_calendar_service_webhook, get_cases_service_webhook

class WhatsAppController(BaseController):
    CONTROLLER_NAME = "webhook"

    @BaseController.get(
        "/hi",
        summary="Get case detail",
    )
    async def cases_get_by_id(
        self,
    ):
        return self.success(result="hi")

    @BaseController.post(
            "/whatsapp",
            summary="Add a new case",
            # response_model=PlainTextResponse[Response],
        )
    async def whatsapp_webhook(
        self,
        request: Request,
        cases_service:CasesService = Depends(get_cases_service_webhook),
        calendar_service:CalendarService = Depends(get_calendar_service_webhook),
    ):
        data = await request.form()

        phone = data.get("From")
        message = data.get("Body")
        
        # Validate & narrow types
        if not isinstance(phone, str) or not phone:
            raise HTTPException(400, "Missing or invalid 'From'")
        if not isinstance(message, str):
            message = str(message) if message else ""

        reply = await handle_message(phone, message, cases_service, calendar_service)

        return PlainTextResponse(reply)