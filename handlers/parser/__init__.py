from termcolor import cprint

from handlers.parser.StrMobileMain import StrMobileMain


class ParserMain:
    """Класс парсера"""

    def __init__(self) -> None:
        self.str_mobile_main = StrMobileMain()

    def get_site_class(self, site: str):
        """Запускает пармер нужного сайта"""

        if site == "str_mobile":
            self.str_mobile_main()
        else:
            cprint("Такого сайта нету!", "light_red")
