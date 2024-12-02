#!/usr/bin/python3

import os
import glob
import json

def gather_desktop_files():
    # Ścieżki do katalogów z plikami .desktop
    desktop_dirs = [
        "/usr/share/applications",
        os.path.expanduser("~/.local/share/applications")
    ]

    desktop_files = []
    for dir_path in desktop_dirs:
        if os.path.exists(dir_path):
            desktop_files.extend(glob.glob(os.path.join(dir_path, "*.desktop")))

    return desktop_files

def extract_app_names(desktop_files):
    app_names = []
    for file_path in desktop_files:
        app_name = os.path.basename(file_path)
        if app_name.endswith(".desktop"):
            app_names.append(app_name)

    return sorted(app_names)

def generate_app_picker_layout(app_names):
    # Generowanie listy aplikacji bez grup
    layout = [{"apps": app_names}]
    return json.dumps(layout, indent=4)

if __name__ == "__main__":
    # Pobranie plików .desktop
    desktop_files = gather_desktop_files()

    # Wyciągnięcie i posortowanie nazw aplikacji
    app_names = extract_app_names(desktop_files)

    # Generowanie układu dla klucza dconf
    app_picker_layout = generate_app_picker_layout(app_names)

    print("Wartość dla klucza org.gnome.shell app-picker-layout:")
    print(app_picker_layout)

    print("\nAby ustawić klucz, użyj polecenia:")
    print("gsettings set org.gnome.shell app-picker-layout '{layout}'".format(layout=app_picker_layout))
