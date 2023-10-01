import json
from pathlib import Path

from handlers.GroupsUpdate.GroupUpdateMain import GroupUpdateMain
from termcolor import cprint

from utils.create_dir import PATH_PROJECT


class GroupsUpdateMain:
    """Основной класс групп обновлений"""

    def __init__(self):
        # Файл со списками товаров групп
        self.path_file_groups = PATH_PROJECT / Path("groups_update.json")
        if not self.path_file_groups.exists():
            self.edit_file_group({})

    def start_group_update(self, name_group: str):
        """Запуск группы обновления"""

        dict_parser = self.get_groups_updates()

        if dict_parser.get(name_group):
            dict_parser_group = dict_parser[name_group]
        else:
            cprint("Такой группы нету!", "light_red")
            return

        cur_group_update = GroupUpdateMain(
            name_group=name_group, dict_parser=dict_parser_group
        )
        cur_group_update()

        groups_update = self.get_groups_updates()
        groups_update[name_group] = dict_parser_group
        self.edit_file_group(groups_update=groups_update)

    def get_groups_updates(self):
        """Получение списков товаров групп"""

        file_groups = open(self.path_file_groups, "r", encoding="utf-8")
        groups_updates: dict = json.loads(file_groups.read())

        return groups_updates

    def create_group(self, name_group: str):
        """Создание группы"""

        groups_update = self.get_groups_updates()

        if name_group not in groups_update:
            groups_update[name_group] = {
                "products": {"ids": [], "articles": [], "codes": []},
                "categories": [],
            }

            self.edit_file_group(groups_update=groups_update)
            cprint(f'Группа "{name_group}" создана.', "light_blue")
            return True
        else:
            cprint(f'Группа "{name_group}" уже существует.', "light_red")
            return False

    def edit_file_group(self, groups_update: dict):
        """Изменение списков товаров групп"""

        with open(self.path_file_groups, "w", encoding="utf-8") as file:
            json.dump(groups_update, file, ensure_ascii=False)
