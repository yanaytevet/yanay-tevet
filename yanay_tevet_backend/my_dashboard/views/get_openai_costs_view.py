import datetime
import logging
from typing import Type

import httpx
from ninja import Schema, Query, Path as NinjaPath

from django.conf import settings

from common.simple_api.api_request import APIRequest
from common.simple_api.enums.status_code import StatusCode
from common.simple_api.exceptions.rest_api_exception import RestAPIException
from common.simple_api.views.simple_views.simple_get_api_view import SimpleGetAPIView

logger = logging.getLogger(__name__)

OPENAI_COSTS_URL = 'https://api.openai.com/v1/organization/costs'


class OpenAICostsOutput(Schema):
    currency: str
    month_to_date: float
    last_30_days: float
    last_7_days: float
    today: float
    fetched_at: str


class GetOpenAICostsView(SimpleGetAPIView):
    @classmethod
    def get_output_schema(cls) -> Type[Schema]:
        return OpenAICostsOutput

    @classmethod
    async def check_permitted(cls, api_request: APIRequest, query: Query = None, path: NinjaPath = None) -> None:
        user = await api_request.future_user
        if user is None or user.is_anonymous or not user.is_admin():
            raise RestAPIException(
                status_code=StatusCode.HTTP_403_FORBIDDEN,
                message='Admin only.',
                error_code='admin_only',
            )

    @classmethod
    async def get_data(cls, api_request: APIRequest, query: Query = None, path: NinjaPath = None) -> OpenAICostsOutput:
        api_key = settings.OPENAI_ADMIN_API_KEY
        if not api_key:
            raise RestAPIException(
                status_code=StatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
                message='OPENAI_ADMIN_API_KEY is not configured on the backend.',
                error_code='openai_admin_key_missing',
            )

        now = datetime.datetime.now(datetime.timezone.utc)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_30_days = start_of_today - datetime.timedelta(days=29)
        start_7_days = start_of_today - datetime.timedelta(days=6)

        window_start = min(start_of_month, start_30_days)
        buckets = await cls._fetch_daily_costs(api_key, int(window_start.timestamp()), int(now.timestamp()))

        currency = 'usd'
        month_to_date = 0.0
        last_30_days = 0.0
        last_7_days = 0.0
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
                if bucket_start >= start_30_days:
                    last_30_days += value
                if bucket_start >= start_7_days:
                    last_7_days += value
                if bucket_start >= start_of_today:
                    today += value

        return OpenAICostsOutput(
            currency=currency,
            month_to_date=round(month_to_date, 4),
            last_30_days=round(last_30_days, 4),
            last_7_days=round(last_7_days, 4),
            today=round(today, 4),
            fetched_at=now.isoformat(),
        )

    @classmethod
    async def _fetch_daily_costs(cls, api_key: str, start_time: int, end_time: int) -> list[dict]:
        # OpenAI Admin API paginates large windows; loop until has_more is False.
        headers = {'Authorization': f'Bearer {api_key}'}
        buckets: list[dict] = []
        next_page: str | None = None

        async with httpx.AsyncClient(timeout=20.0) as client:
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
