#!/usr/bin/python3
import os
import glob
import argparse
import subprocess

def get_current_theme():
    # Odczytaj aktualny motyw z pliku settings.ini
    settings_path = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
    if not os.path.exists(settings_path):
        return None
    with open(settings_path, 'r') as f:
        for line in f:
            if line.startswith("gtk-theme-name"):
                return line.split('=')[1].strip()
    return None

def find_icon(icon_name):
    icon_dirs = ["/usr/share/icons"]
    icon_extensions = ['.png', '.svg']
    current_theme = get_current_theme()
    if current_theme:
        theme_dir = os.path.join("/usr/share/icons", current_theme)
        if os.path.exists(theme_dir):
            icon_dirs.append(theme_dir)
    for icon_dir in icon_dirs:
        for ext in icon_extensions:
            icon_path_pattern = os.path.join(icon_dir, '**', f"{icon_name}{ext}")
            matching_files = glob.glob(icon_path_pattern, recursive=True)
            if matching_files:
                return matching_files[0]  # Zwróć pierwszy znaleziony plik
    return None

def display_icon(icon_path):
    try:
        subprocess.run(['xdg-open', icon_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        print(f"Nie można otworzyć ikony: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wyszukaj i wyświetl ikonę.")
    parser.add_argument("icon_name", type=str, help="Nazwa ikony do wyszukania")    
    args = parser.parse_args()
    print("Motyw GTK3:", get_current_theme())
    icon_path = find_icon(args.icon_name)
    if icon_path:
        print(f"Znaleziono ikonę: {icon_path}")
        display_icon(icon_path)
    else:
        print("Ikona nie została znaleziona.")
