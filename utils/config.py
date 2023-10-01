import configparser
import os
from pathlib import Path

from prompt_toolkit.styles import Style
from telebot import TeleBot
from utils.create_dir import PATH_PROJECT
from utils.db_api.handlers import warehouse as db_warehouses


class Configurate:
    """Класс конфигурации"""

    def __init__(self):
        self.path_config: str = PATH_PROJECT / Path("config.ini")
        if not os.path.exists(self.path_config):
            self.create()

        self.config = self.read()

    def create(self):
        """Создание конфигурации"""

        def text_bool(text: str) -> bool:
            bools_dict = {"Да": True, "Нет": False}
            if text in bools_dict:
                bool_text = bools_dict[text]
            return bool_text

        # OzonUpload
        city = input("Введите город ЕКБ/МСК: ")
        notification = text_bool(input("Бот должен уведомлять? Да/Нет: "))

        # TelegramBot
        token = input("Введите токен бота: ")
        chat_id = input("Введите id чата: ")
        topic_id = (
            input("Введите id сообщения о создании темы чата, если есть:\n") or "None"
        )

        config = configparser.ConfigParser()

        config["OzonUpload"] = {
            "city": city,
            "notification": notification,
        }

        config["TelegramBot"] = {
            "token": token,
            "chat_id": chat_id,
            "topic_id": topic_id,
        }


        self.config = config
        self.save()

    def save(self):
        """Сохранение конфигурации"""

        with open(self.path_config, "w", encoding="utf-8") as configfile:
            self.config.write(configfile)

    def read(self):
        """Чтение конфигурации"""

        config = configparser.ConfigParser()
        config.read(self.path_config, encoding="utf-8")
        return config

    def edit(self, name_settings: str, parameter: str, value: str):
        """Редактирование конфигурации"""

        self.config[name_settings][parameter] = value
        self.save()


config = Configurate().config
OzonUpload = config["OzonUpload"]
TelegramBot = config["TelegramBot"]

city, notification = OzonUpload["city"], OzonUpload.getboolean("notification")

token, chat_id, topic_id = (
    TelegramBot["token"],
    TelegramBot["chat_id"],
    TelegramBot["topic_id"],
)


sklads_names = {
    "STR": db_warehouses.get_warehouse(WarehouseName="ST"),
    "ЕКБ": db_warehouses.get_warehouse(WarehouseName="Absol"),
    "МСК": db_warehouses.get_warehouse(WarehouseName="MSK"),
}

style = Style.from_dict(
    {"project": "green", "at": "red", "module": "blue", "sign_more": "white"}
)

bot = TeleBot(token=token)
