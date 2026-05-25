import datetime
import logging
from typing import Any

import httpx
from pydantic import BaseModel

from django.conf import settings

from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException

logger = logging.getLogger(__name__)

OPENAI_COSTS_URL = 'https://api.openai.com/v1/organization/costs'


class OpenAICostsSummary(BaseModel):
    currency: str
    today: float
    month_to_date: float
    fetched_at: str


class OpenAICostsManager:
    async def get_summary(self) -> OpenAICostsSummary:
        api_key = settings.OPENAI_ADMIN_API_KEY
        if not api_key:
            raise RestAPIException(
                status_code=StatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                message='OPENAI_ADMIN_API_KEY is not configured on the backend.',
                error_code='openai_admin_key_missing',
            )

        headers = {'Authorization': f'Bearer {api_key}'}
        now = datetime.datetime.now(datetime.timezone.utc)

        async with httpx.AsyncClient(timeout=20.0) as client:
            costs = await self._fetch_costs_window(client, headers, now)

        return OpenAICostsSummary(
            currency=costs['currency'],
            today=costs['today'],
            month_to_date=costs['month_to_date'],
            fetched_at=now.isoformat(),
        )

    async def _fetch_costs_window(
        self,
        client: httpx.AsyncClient,
        headers: dict[str, str],
        now: datetime.datetime,
    ) -> dict[str, Any]:
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        buckets = await self._fetch_daily_costs(
            client,
            headers,
            int(start_of_month.timestamp()),
            int(now.timestamp()),
        )

        currency = 'usd'
        month_to_date = 0.0
        today = 0.0

        for bucket in buckets:
            bucket_start = datetime.datetime.fromtimestamp(bucket['start_time'], tz=datetime.timezone.utc)
            for result in bucket.get('results') or []:
                amount = result.get('amount') or {}
                value = float(amount.get('value', 0.0))
                if amount.get('currency'):
                    currency = amount['currency']
                if bucket_start >= start_of_month:
                    month_to_date += value
                if bucket_start >= start_of_today:
                    today += value

        return {
            'currency': currency,
            'today': round(today, 4),
            'month_to_date': round(month_to_date, 4),
        }

    async def _fetch_daily_costs(
        self,
        client: httpx.AsyncClient,
        headers: dict[str, str],
        start_time: int,
        end_time: int,
    ) -> list[dict]:
        buckets: list[dict] = []
        next_page: str | None = None

        while True:
            params: dict[str, str | int] = {
                'start_time': start_time,
                'end_time': end_time,
                'bucket_width': '1d',
                'limit': 31,
            }
            if next_page:
                params['page'] = next_page

            response = await client.get(OPENAI_COSTS_URL, headers=headers, params=params)
            if response.status_code != 200:
                logger.error(f'OpenAI costs API returned {response.status_code}: {response.text}')
                raise RestAPIException(
                    status_code=StatusCode.HTTP_502_BAD_GATEWAY,
                    message=f'OpenAI API returned {response.status_code}.',
                    error_code='openai_api_error',
                )

            payload = response.json()
            buckets.extend(payload.get('data') or [])

            if not payload.get('has_more'):
                break
            next_page = payload.get('next_page')
            if not next_page:
                break

        return buckets
