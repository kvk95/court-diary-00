"""reports_controller.py — HTTP routes for Reports module"""

from fastapi import Depends

from app.api.v1.routes.base.base_controller import BaseController
from app.dependencies import get_reports_service
from app.dtos.base.base_out_dto import BaseOutDto
from app.dtos.reports_dto import ReportsDashboardOut
from app.services.reports_service import ReportsService


class ReportsController(BaseController):
    CONTROLLER_NAME = "reports"

    @BaseController.get(
        "/dashboard",
        summary="Full reports dashboard — cases, hearings, billing analytics",
        response_model=BaseOutDto[ReportsDashboardOut],
    )
    async def reports_get_dashboard(
        self,
        service: ReportsService = Depends(get_reports_service),
    ) -> BaseOutDto[ReportsDashboardOut]:
        return self.success(result=await service.reports_get_dashboard())
