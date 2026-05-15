import logging

from asgiref.sync import sync_to_async
from openai import OpenAI

from django.conf import settings

from common.generative_ai.enums.generative_ai_model import GenerativeAiModel
from common.generative_ai.enums.image_size import ImageSize
from common.generative_ai.enums.image_quality import ImageQuality

logger = logging.getLogger(__name__)


class ImageGenerativeAI:
    @classmethod
    async def generate_image(
        cls,
        prompt: str,
        size: ImageSize = ImageSize.SQUARE_1024,
        quality: ImageQuality = ImageQuality.MEDIUM,
        model: GenerativeAiModel = GenerativeAiModel.GPT_IMAGE_1,
    ) -> str:
        try:
            return await cls._async_generate_image(prompt, size, quality, model)
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            raise

    @classmethod
    @sync_to_async
    def _async_generate_image(
        cls,
        prompt: str,
        size: ImageSize,
        quality: ImageQuality,
        model: GenerativeAiModel,
    ) -> str:
        client = OpenAI(api_key=settings.CHATGPT_API_KEY)
        response = client.images.generate(
            model=model.value,
            prompt=prompt,
            size=size.value,
            quality=quality.value,
            n=1,
        )
        return response.data[0].b64_json
