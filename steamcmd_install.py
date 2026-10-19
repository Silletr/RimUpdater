from os import getenv
from pathlib import Path

from loguru import logger

logger.add("steamcmd_installer.log", colorize=True)


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    Define SteamCMD .exe file    ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
def define_smd(path: str | None):
    path = getenv("SteamCMD")
    if not path:
        logger.critical("SteamCMD isn't found, define it in your Windows PATH!")
    return path


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    Download to divided folder, to copy-paste after Rim's folder is defined    ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
def download_to_temp(path: Path | None = None, mods_folder: str | None = None):
    # Command to use:
    """
    login anonymous <- to login into SteamCMD
    workshop_download_item 294100 X <- where 294100 = Rimworld SteamID, X = Mod WorkshopID
    validate <- to make sure everything installed just as need I think (if u want)
    """
    if path is None:
        path = Path.home() / "RimUpdater" / "temp"
        return path

    mods_folder = input("Enter Rimworld's Mods folder path (absolute): ")
    logger.info(f"Installed mods path: {mods_folder} | Folder to save new mods: {path}")


download_to_temp()
