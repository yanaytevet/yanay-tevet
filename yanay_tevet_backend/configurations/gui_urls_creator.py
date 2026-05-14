

class GuiUrlsCreator:
    def __init__(self, with_hostname: bool = True):
        self.with_hostname = with_hostname
        self.hostname = 'self.gui_conf.get_gui_hostname()' if with_hostname else '/'

    def get_main_page(self) -> str:
        return self.hostname
