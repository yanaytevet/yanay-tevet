from common.base_enum import BaseEnum


class NodeStatus(BaseEnum):
    STUB = 'stub'
    GENERATING = 'generating'
    NEEDS_REVIEW = 'needs_review'
    PUBLISHED = 'published'
