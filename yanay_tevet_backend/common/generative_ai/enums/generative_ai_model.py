from common.base_enum import BaseEnum


class GenerativeAiModel(BaseEnum):
    # Text models
    GPT_4_1 = 'gpt-4.1'
    GPT_4_1_MINI = 'gpt-4.1-mini'
    GPT_4_1_NANO = 'gpt-4.1-nano'
    GPT_4O = 'gpt-4o'
    GPT_4O_MINI = 'gpt-4o-mini'
    O4_MINI = 'o4-mini'
    O3 = 'o3'
    O3_MINI = 'o3-mini'
    O1 = 'o1'

    # Image models
    GPT_IMAGE_1 = 'gpt-image-1'
    DALL_E_3 = 'dall-e-3'
    DALL_E_2 = 'dall-e-2'
