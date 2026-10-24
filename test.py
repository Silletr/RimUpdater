from steamcmd_install import download_to_temp, spawn_steamcmd

if __name__ == "__main__":
    result = download_to_temp()
    if result is not None:
        path_to_save, mods_folder, mods_list = result
        # Download into the temp folder
        spawn_steamcmd(mods_list, install_dir=path_to_save)
