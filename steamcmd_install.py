from pathlib import Path
from subprocess import run, CalledProcessError
from shutil import which
from tkinter import Tk, filedialog
from loguru import logger

logger.add("steamcmd_installer.log", colorize=True)


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    Define SteamCMD .exe file    ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
def define_smd():
    path = which("steamcmd.exe")
    if not path:
        logger.critical("SteamCMD isn't found in your PATH!")
        raise FileNotFoundError("SteamCMD executable isn't in your PATH!")
    if path:
        logger.info(f"SteamCMD found at: {path}")
    return path


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    Define function to select folder with Rim's mods' folder later             ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


def select_folder() -> Path | None:
    root = Tk()
    root.withdraw()

    try:
        folder = filedialog.askdirectory(
            title="Select RimWorld mods folder",
            mustexist=True,
        )
        return Path(folder) if folder else None
    finally:
        root.destroy()


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    Get installed RimWorld Workshop mods                                       ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛


def get_installed_mods(mods_folder: Path) -> list[int]:
    return [
        int(folder.name)
        for folder in mods_folder.iterdir()
        if folder.is_dir() and folder.name.isdigit()
    ]


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    Download to divided folder, to copy-paste after Rim's folder is defined    ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
def download_to_temp(
    path_to_save: Path | None = None,
    mods_folder: Path | None = None,
) -> tuple[Path, Path, list[int]] | None:
    if path_to_save is None:
        path_to_save = Path.home() / "RimUpdater" / "temp"
        path_to_save.mkdir(parents=True, exist_ok=True)
    if mods_folder is None:
        mods_folder = select_folder()

        if mods_folder is None:
            logger.warning("Folder selection cancelled.")
            return None

    mods_list = get_installed_mods(mods_folder)

    logger.info(
        f"Installed mods folder: {mods_folder} | "
        f"Temporary folder: {path_to_save} | "
        f"Found {len(mods_list)} mods"
    )

    return path_to_save, mods_folder, mods_list


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    Spawn one process of SteamCMD defined from define_smd() function           ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
def spawn_steamcmd(mods_list: list[int]) -> None:
    steamcmd_path = define_smd()

    commands = ["login anonymous"]

    for workshop_id in mods_list:
        commands.append(f"workshop_download_item 294100 {workshop_id}")
        logger.info(
            f"Mod {workshop_id} added to download queue\nCommand: {commands[-1]}"
        )

    # SteamCMD accepts commands through its standard input
    command_input = "\n".join(commands) + "\nquit\n"

    try:
        run(
            [steamcmd_path],
            input=command_input,
            text=True,
            check=True,
        )
    except CalledProcessError as e:
        logger.error(f"SteamCMD process failed: {e}")
        logger.error(e.stderr or e.stdout or "No output available")
        raise


if __name__ == "__main__":
    result = download_to_temp()

    if result is not None:
        path_to_save, mods_folder, mods_list = result

        spawn_steamcmd(mods_list)
