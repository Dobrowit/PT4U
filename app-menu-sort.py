#!/usr/bin/python3

import os
import glob
import configparser

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

def extract_app_names(desktop_files, lang):
    app_names = []

    for file_path in desktop_files:
        config = configparser.ConfigParser(interpolation=None, delimiters=('=',))
        config.optionxform = str  # Zachowaj wielkość liter w kluczach
        try:
            config.read(file_path, encoding="utf-8")
            name_field = f"Name[{lang}]" if lang else "Name"
            name = config["Desktop Entry"].get(name_field, None) or config["Desktop Entry"].get("Name", None)
            if name:
                app_names.append((name, os.path.basename(file_path)))
        except Exception as e:
            # Pomijamy pliki, których nie można poprawnie odczytać
            continue

    # Sortowanie po nazwach (pierwszy element krotki)
    return sorted(app_names, key=lambda x: x[0])

def generate_app_picker_layout(app_names):
    # Generowanie wartości klucza zgodnie z wymaganym formatem
    layout = []
    for position, (_, app_file) in enumerate(app_names):
        layout.append(f"'{app_file}': <{{'position': <{position}>}}>")
    return f"[{', '.join(layout)}]"

if __name__ == "__main__":
    # Pobranie preferowanego języka od użytkownika
    lang = input("Podaj kod języka (np. 'pl' dla polskiego) lub naciśnij Enter dla domyślnego: ").strip()

    # Pobranie plików .desktop
    desktop_files = gather_desktop_files()

    # Wyciągnięcie i posortowanie nazw aplikacji
    app_names = extract_app_names(desktop_files, lang)

    # Generowanie układu dla klucza dconf
    app_picker_layout = generate_app_picker_layout(app_names)

    print("Wartość dla klucza org.gnome.shell app-picker-layout:")
    print(app_picker_layout)

    print("\nAby ustawić klucz, użyj polecenia:")
    print(f"gsettings set org.gnome.shell app-picker-layout \"{app_picker_layout}\"")
