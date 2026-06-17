from common.base_enum import BaseEnum


class NodeType(BaseEnum):
    PASSAGE = 'passage'
    SENTENCE = 'sentence'
    WORD = 'word'
    KANJI = 'kanji'
    PARTICLE = 'particle'
    RULE = 'rule'
