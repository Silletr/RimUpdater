from pathlib import Path
from subprocess import run
from shutil import which
from tkinter import Tk, filedialog
from loguru import logger
from time import sleep

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
    mods = []

    for folder in mods_folder.iterdir():
        if not folder.is_dir():
            continue

        if folder.name.isdigit():
            mods.append(int(folder.name))
        else:
            logger.warning(
                f"Skipping non-numeric folder: {folder.name}. "
                "Please reinstall it manually — I only handle Workshop mods!"
            )

    return mods


#    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#    ┃    Download to divided folder, to copy-paste after Rim's folder is defined    ┃
#    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
def download_to_temp(
    path_to_save: Path | None = None,
    mods_folder: Path | None = None,
) -> tuple[Path, Path, list[int]] | None:
    # Command to use:
    """
    login anonymous <- to login into SteamCMD
    workshop_download_item 294100 X <- where 294100 = Rimworld SteamID, X = Mod WorkshopID
    validate <- to make sure everything installed just as need I think (if u want)

    !!! VALIDATE IS TEMPORARIRLY DISABLED, BECAUSE I'M TESTING EVERYTHING, VALIDATION WILL BE THEL LAST THING I'LL ADD !!!
    """
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
def spawn_steamcmd(
    mods_list: list[int], install_dir: Path | None = None, batch_size: int = 8
) -> None:
    steamcmd_path = define_smd()

    for i in range(0, len(mods_list), batch_size):
        batch = mods_list[i : i + batch_size]
        logger.info(
            f"=== Batch {i // batch_size + 1}/{(len(mods_list) + batch_size - 1) // batch_size} "
            f"({len(batch)} mods) ==="
        )

        args = [
            steamcmd_path,
            "+@ShutdownOnFailedCommand",
            "0",
        ]

        # force_install_dir must go before logon
        if install_dir is not None:
            args += ["+force_install_dir", str(install_dir)]

        args += ["+login", "anonymous"]

        for workshop_id in batch:
            args += ["+workshop_download_item", "294100", str(workshop_id)]

        args.append("+quit")

        try:
            result = run(
                args,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(f"Batch finished with code {result.returncode}")
            else:
                logger.success(f"Batch {i // batch_size + 1} finished")

        except Exception as e:
            logger.exception(f"Batch failed: {e}")

        if i + batch_size < len(mods_list):
            logger.info("Waiting 5 seconds before next batch...")
            sleep(5)
