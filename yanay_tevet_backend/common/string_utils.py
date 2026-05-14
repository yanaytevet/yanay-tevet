import random
import re
import string


class StringUtils:
    @classmethod
    def create_random_hash(cls, hash_length: int) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=hash_length))

    @classmethod
    def lower_case_to_camel_case(cls, str1: str) -> str:
        s = re.sub(r"(_|-)+", " ", str1).title().replace(" ", "")
        return ''.join([s[0].lower(), s[1:]])

    @classmethod
    def pascal_case_to_lower_case(cls, str1: str) -> str:
        s = re.sub(r"(?<!^)(?=[A-Z])", "_", str1).lower()
        return ''.join([s[0].lower(), s[1:]])
