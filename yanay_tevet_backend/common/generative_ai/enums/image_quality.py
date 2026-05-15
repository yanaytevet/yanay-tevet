from common.base_enum import BaseEnum


class ImageQuality(BaseEnum):
    # DALL-E 3
    STANDARD = 'standard'
    HD = 'hd'
    # gpt-image-1
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    AUTO = 'auto'
