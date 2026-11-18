from common.base_enum import BaseEnum


# The site languages. Adding one means a strings file for it in every translated area of the web app
# (docs/frontend.md, Language); the compiler then lists what is missing.
class Language(BaseEnum):
    ENGLISH = 'en'
    HEBREW = 'he'
    GERMAN = 'de'
    SPANISH = 'es'
    FRENCH = 'fr'
    RUSSIAN = 'ru'
    ARABIC = 'ar'
    JAPANESE = 'ja'
    CHINESE_SIMPLIFIED = 'zh-Hans'
