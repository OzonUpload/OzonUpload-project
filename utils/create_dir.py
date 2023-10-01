import os
import platform
from pathlib import Path

match platform.system():
    case "Linux" | "Darvin":
        env_path = os.getenv("HOME")
    case "Windows":
        env_path = os.getenv("APPDATA")

PATH_PROJECT = Path(env_path) / Path("OzonUpload")
PATH_HISTORY = PATH_PROJECT / Path("history")
PATH_HISTORY_GROUPS_UPDATE = PATH_PROJECT / Path("history/groups_update")

if not PATH_PROJECT.exists():
    PATH_PROJECT.mkdir()
    PATH_HISTORY.mkdir()
    PATH_HISTORY_GROUPS_UPDATE.mkdir()
