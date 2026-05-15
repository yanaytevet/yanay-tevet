import logging
from typing import Type, TypeVar

from asgiref.sync import sync_to_async
from openai import OpenAI
from pydantic import BaseModel

from django.conf import settings

from common.generative_ai.enums.generative_ai_model import GenerativeAiModel

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class TextGenerativeAI:
    @classmethod
    async def generate_text(
        cls,
        prompt: str,
        model_type: GenerativeAiModel = GenerativeAiModel.GPT_4O,
        system_prompt: str = "You are a helpful assistant."
    ) -> str:
        try:
            return await cls._async_generate_text(prompt, model_type, system_prompt)
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    @classmethod
    async def generate_schema(
        cls,
        prompt: str,
        schema_cls: Type[T],
        model_type: GenerativeAiModel = GenerativeAiModel.GPT_4O,
        system_prompt: str = "You are a helpful assistant."
    ) -> T:
        try:
            return await cls._async_generate_schema(prompt, schema_cls, model_type, system_prompt)
        except Exception as e:
            logger.error(f"Error generating schema: {e}")
            raise

    @classmethod
    @sync_to_async
    def _async_generate_text(cls, prompt: str, model_type: GenerativeAiModel, system_prompt: str) -> str:
        client = OpenAI(api_key=settings.CHATGPT_API_KEY)
        response = client.chat.completions.create(
            model=model_type.value,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content

    @classmethod
    @sync_to_async
    def _async_generate_schema(cls, prompt: str, schema_cls: Type[T], model_type: GenerativeAiModel, system_prompt: str) -> T:
        client = OpenAI(api_key=settings.CHATGPT_API_KEY)
        response = client.beta.chat.completions.parse(
            model=model_type.value,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            response_format=schema_cls,
        )
        return response.choices[0].message.parsed
