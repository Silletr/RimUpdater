from install_mod import get_workshop_path, move_mods_to_rim
from steamcmd_install import download_to_temp, spawn_steamcmd


def main():
    result = download_to_temp()

    if result is not None:
        path_to_save, mods_folder, mods_list = result

        spawn_steamcmd(
            mods_list=mods_list,
            mods_folder=mods_folder,
            install_dir=path_to_save,
        )

        path_to_contents = get_workshop_path()
        move_mods_to_rim(path_to_contents)


if __name__ == "__main__":
    main()
