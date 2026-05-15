from common.base_enum import BaseEnum


class ImageSize(BaseEnum):
    # DALL-E 3 and gpt-image-1
    SQUARE_1024 = '1024x1024'
    # DALL-E 3
    WIDE_1792 = '1792x1024'
    TALL_1024 = '1024x1792'
    # gpt-image-1
    WIDE_1536 = '1536x1024'
    TALL_1536 = '1024x1536'
    AUTO = 'auto'
