
class UrlsUtils:
    @classmethod
    def fix_url(cls, url: str) -> str:
        url = url.strip('/')
        if not url:
            return url
        if not url.endswith('/'):
            url += '/'
        while '//' in url:
            url = url.replace('//', '/')
        return url
