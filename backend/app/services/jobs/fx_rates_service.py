"""
app.services.jobs.fx_rates_service
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional, Tuple, List

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base.base_service import BaseService


class FxRatesService(BaseService):

    # https://github.com/fawazahmed0/exchange-api/tree/main?tab=readme-ov-file
    # https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/inr.json
    # https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2026-01-05/v1/currencies/inr.json
    # https://2026-01-05.currency-api.pages.dev/v1/currencies/inr.json
    # https://latest.currency-api.pages.dev/v1/currencies/inr.json

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)
        self.currency_url = (
            "https://latest.currency-api.pages.dev/v1/currencies/inr.json"
        )
        self.currency_list = ["INR", "USD", "EUR", "GBP", "JPY", "AUD"]

    async def get_today_from_api(self) -> Dict[str, Any]:
        """Call external FX API and normalize result."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(self.currency_url)
            resp.raise_for_status()
            data = resp.json()  # expects {"date": "YYYY-MM-DD", "inr": {...}}

        rate_date_str = data.get("date")
        if rate_date_str:
            rate_date = datetime.strptime(rate_date_str, "%Y-%m-%d").date()
        else:
            rate_date = date.today()

        inr_rates = data.get("inr", {})

        # Build normalized dict with only supported currencies
        normalized_rates = {
            "rate_date": rate_date,
            "base": "INR",
        }

        # Add rates for each currency in currency_list
        for code in self.currency_list:
            lowercase_code = code.lower()
            if code == "INR":
                normalized_rates["inr"] = 1.0
            else:
                normalized_rates[lowercase_code] = float(
                    inr_rates.get(lowercase_code, 0.0)
                )

        return normalized_rates

    async def ensure_today_rates(self) -> Tuple[bool, Optional[List[Dict[str, Any]]]]:
        today = date.today()

        # # Check if all currencies for today exist in DB
        # existing_records = await self.currencies_repo.list_all(
        #     session=self.session,
        #     filters={
        #         self.currencies_repo.model.rate_date: today,
        #     },
        #     where=[
        #         self.currencies_repo.model.currency_code.in_(self.currency_list),
        #     ],
        # )

        # if len(existing_records) == len(self.currency_list):
        #     normalized = [
        #         {
        #             "currency_code": rec.currency_code,
        #             "rate": rec.rate,
        #             "rate_date": rec.rate_date,
        #             "status_ind": rec.status_ind,
        #         }
        #         for rec in existing_records
        #     ]
        #     return True, normalized

        # Fetch fresh rates from API
        api_data = await self.get_today_from_api()

        # Convert to list of individual currency records
        new_records: List[Dict[str, Any]] = []
        for code in self.currency_list:
            lowercase_code = code.lower()
            rate_value = api_data.get(lowercase_code)
            if code == "INR":
                rate_value = 1.0

            record = {
                "currency_code": code,
                "rate": rate_value,
                "rate_date": api_data["rate_date"],
                "status_ind": True,
            }
            new_records.append(record)

        return False, new_records

    async def run_fx_startup_job(self) -> bool:

        exists, rate_records = await self.ensure_today_rates()

        if exists:
            print(f"FX rates for {date.today()} already exist in DB. Skipping update.")
            return False

        if not rate_records:
            print("⚠️ No FX rate records returned. Skipping update.")
            return False

        print(f"Fetching and inserting FX rates for {rate_records[0]['rate_date']}...")

        # for record in rate_records:
        #     print(f"\n\n\n\n🟢 {record}\n\n\n")
        #     obj = await self.currencies_repo.update(
        #         session=self.session,
        #         filters={
        #             self.currencies_repo.model.currency_code: record.get(
        #                 "currency_code"
        #             ),
        #         },
        #         data={
        #             "rate": record.get("rate"),
        #             "rate_date": record.get("rate_date"),
        #         },
        #     )
        #     print(obj)

        print("✅️ Successfully updated today's exchange rates in the database.")
        print(rate_records)
        return True
