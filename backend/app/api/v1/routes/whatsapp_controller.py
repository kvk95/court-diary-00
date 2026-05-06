# app/whatsapp/webhook.py

from fastapi import HTTPException, Depends, Request
from fastapi.responses import PlainTextResponse

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import (
    get_whatsapp_service_webhook,
)
from app.whatsapp.handler import WhatsAppService


class WhatsAppController(BaseController):
    CONTROLLER_NAME = "webhook"

    @BaseController.get("/hi", summary="Health check")
    async def hi(self):
        return self.success(result="hi")

    @BaseController.post("/whatsapp", summary="WhatsApp webhook (Twilio)")
    async def whatsapp_webhook(
        self,
        request: Request,
        whatsapp_service: WhatsAppService = Depends(get_whatsapp_service_webhook),
    ):
        data = await request.form()

        phone = data.get("From")
        message = data.get("Body")

        if not isinstance(phone, str) or not phone:
            raise HTTPException(400, "Missing or invalid 'From'")
        if not isinstance(message, str):
            message = message.strip() if isinstance(message, str) else ""

        phone = phone.replace("whatsapp:", "").strip()

        reply = await whatsapp_service.handle_message(
            phone=phone,
            message=message,
        )

        return PlainTextResponse(reply)