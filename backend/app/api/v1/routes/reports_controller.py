# app/api/v1/routes/reports/reports_controller.py

from fastapi import Depends

from app.api.v1.routes.base.base_controller import BaseController

from app.dependencies import get_reports_service

from app.dtos.base.base_out_dto import BaseOutDto

from app.dtos.reports_dto import (
    CaseFilingTrendReportOut,
    ChamberGrowthReportOut,
    LoginAnalyticsReportOut,
)

from app.services.reports_service import ReportsService

from app.auth.permissions import require_permission, PType

from app.database.models.refm_modules import RefmModulesEnum


_SUAD = RefmModulesEnum.SUPER_USER


class ReportsController(BaseController):

    CONTROLLER_NAME = "reports"

    @BaseController.get(
        "/chamber-growth",
        summary="Chamber growth report",
        response_model=BaseOutDto[ChamberGrowthReportOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_chamber_growth_report(
        self,
        service: ReportsService = Depends(
            get_reports_service
        ),
    ):
        return self.success(
            result=await service.get_chamber_growth_report()
        )
    
    @BaseController.get(
        "/login-analytics",
        summary="Login analytics report",
        response_model=BaseOutDto[LoginAnalyticsReportOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_login_analytics_report(
        self,
        service: ReportsService = Depends(
            get_reports_service
        ),
    ):
        return self.success(
            result=await service.get_login_analytics_report()
        )
    
    @BaseController.get(
        "/case-filing-trends",
        summary="Case filing trends report",
        response_model=BaseOutDto[CaseFilingTrendReportOut],
        dependencies=[Depends(require_permission(_SUAD, PType.READ))],
    )
    async def get_case_filing_trend_report(
        self,
        service: ReportsService = Depends(
            get_reports_service
        ),
    ):
        return self.success(
            result=await service.get_case_filing_trend_report()
        )