from ninja import Schema

from japanese.enums.rule_category import RuleCategory


class RuleSchema(Schema):
    name: str
    category: RuleCategory = RuleCategory.OTHER
