from common.base_enum import BaseEnum


class EdgeType(BaseEnum):
    CONTAINS = 'contains'
    COMPOSED_OF = 'composed_of'
    USES_RULE = 'uses_rule'
    EXAMPLE_OF = 'example_of'
    EXCEPTION_TO = 'exception_to'
    SYNONYM_OF = 'synonym_of'
    RELATED_TO = 'related_to'
    SAME_KANJI_AS = 'same_kanji_as'
