from pathlib import Path


def get_desktop_folder():
    home_dir = Path.home()
    desktop_folder = home_dir / 'Desktop'
    return desktop_folder
