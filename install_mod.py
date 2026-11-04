from pathlib import Path
from shutil import move

from loguru import logger

from steamcmd_install import define_smd

log = logger.add(
    sink="install_mod.py.log",
    level="INFO",
    # Format will be later
)


#  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_workshop_path() -> Path:
    steamcmd_path = Path(define_smd())
    return steamcmd_path.parent / "steamapps" / "workshop" / "content" / "294100"


#  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def move_mods_to_rim(path_to_contents: Path) -> None:
    workshop_folder = get_workshop_path()

    for mod_folder in workshop_folder.iterdir():
        if not mod_folder.is_dir():
            continue

        destination = path_to_contents / mod_folder.name
        move(str(mod_folder), str(destination))
