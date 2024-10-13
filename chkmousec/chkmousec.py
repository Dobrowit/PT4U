#!/usr/bin/python3
import os
import configparser
import argparse
import subprocess
#import xml.etree.ElementTree as ET

def check_file_exists(file_path, quiet_mode):
    """Sprawdza, czy plik istnieje i jest czytelny."""
    if os.path.isfile(file_path):
        if not quiet_mode:
            print(f"[INFO] Znaleziono plik: {file_path}")
        return True
    else:
        if not quiet_mode:
            print(f"[INFO] Brak pliku: {file_path}")
        return False

def print_aligned(label, value, label_width=90):
    """Wyświetla tekst w sposób wyrównany do kolumny."""
    print(f"{label.rjust(label_width)}: {value}")

def read_index_theme(file_path, quiet_mode, show_names, show_sizes):
    """Odczytuje ustawienie kursora z pliku index.theme."""
    if check_file_exists(file_path, quiet_mode):
        config = configparser.ConfigParser()
        config.read(file_path)
        if 'Icon Theme' in config and 'Inherits' in config['Icon Theme']:
            if show_names:
                print_aligned(f"Motyw kursora z {file_path}", config['Icon Theme']['Inherits'])
        elif not quiet_mode:
            print(f"[WARN] Plik {file_path} nie zawiera informacji o motywie kursora.")

def read_gtk_settings(file_path, quiet_mode, show_names, show_sizes):
    """Odczytuje ustawienia kursora z plików GTK."""
    if check_file_exists(file_path, quiet_mode):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if 'gtk-cursor-theme-name' in line and show_names:
                    print_aligned(f"Motyw kursora GTK z {file_path}", line.split('=')[1].strip())
                if 'gtk-cursor-theme-size' in line and show_sizes:
                    print_aligned(f"Rozmiar kursora GTK z {file_path}", line.split('=')[1].strip())

def read_kde_settings(file_path, quiet_mode, show_names, show_sizes):
    """Odczytuje ustawienia kursora z pliku KDE (kcminputrc)."""
    if check_file_exists(file_path, quiet_mode):
        config = configparser.ConfigParser()
        config.read(file_path)
        if 'Mouse' in config and 'cursorTheme' in config['Mouse']:
            if show_names:
                print_aligned(f"Motyw kursora KDE z {file_path}", config['Mouse']['cursorTheme'])
        if 'Mouse' in config and 'cursorSize' in config['Mouse'] and show_sizes:
            print_aligned(f"Rozmiar kursora KDE z {file_path}", config['Mouse']['cursorSize'])

def read_qt_settings(file_path, quiet_mode, show_names, show_sizes):
    """Odczytuje ustawienia kursora z pliku qt5ct."""
    if check_file_exists(file_path, quiet_mode):
        config = configparser.ConfigParser()
        config.read(file_path)
        if 'Appearance' in config and 'CursorTheme' in config['Appearance']:
            if show_names:
                print_aligned(f"Motyw kursora Qt z {file_path}", config['Appearance']['CursorTheme'])

def read_lxqt_settings(file_path, quiet_mode, show_names, show_sizes):
    """Odczytuje ustawienia kursora z pliku lxqt.conf."""
    read_qt_settings(file_path, quiet_mode, show_names, show_sizes)

def read_xsettings(file_path, quiet_mode, show_names, show_sizes):
    """Odczytuje ustawienia kursora z pliku xsettings.xml."""
    if check_file_exists(file_path, quiet_mode):
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Szuka linii z nazwą motywu kursora
                    if 'CursorThemeName' in line and show_names:
                        value = line.split('value="')[1].split('"')[0]
                        print_aligned(f"Motyw kursora z {file_path}", value)
                    # Szuka linii z rozmiarem kursora
                    elif 'CursorThemeSize' in line and show_sizes:
                        # Zakłada, że wartość jest 'empty' w przypadku braku rozmiaru
                        if 'empty' in line:
                            value = 'brak'
                        else:
                            value = line.split('value="')[1].split('"')[0]
                        print_aligned(f"Rozmiar kursora z {file_path}", value)
        except Exception as e:
            if not quiet_mode:
                print(f"[ERROR] Błąd podczas odczytu pliku {file_path}: {e}")

def check_dconf(quiet_mode, show_names, show_sizes):
    """Sprawdza ustawienia kursora w dconf."""
    try:
        if show_names:
            cursor_name = subprocess.check_output(['dconf', 'read', '/org/gnome/desktop/interface/cursor-theme']).decode().strip().strip("'")
            print_aligned("Motyw kursora dconf", cursor_name)
        if show_sizes:
            cursor_size = subprocess.check_output(['dconf', 'read', '/org/gnome/desktop/interface/cursor-size']).decode().strip().strip("'")
            print_aligned("Rozmiar kursora dconf", cursor_size)
    except Exception as e:
        if not quiet_mode:
            print(f"[WARN] Nie udało się odczytać ustawień dconf: {e}")

def check_environment_variables(quiet_mode, show_names, show_sizes):
    """Sprawdza zmienne środowiskowe X11."""
    cursor_theme = os.getenv('XCURSOR_THEME')
    cursor_size = os.getenv('XCURSOR_SIZE')
    if cursor_theme and show_names:
        print_aligned("Zmienna środowiskowa XCURSOR_THEME", cursor_theme)
    if cursor_size and show_sizes:
        print_aligned("Zmienna środowiskowa XCURSOR_SIZE", cursor_size)

def main():
    parser = argparse.ArgumentParser(description="Sprawdź ustawienia kursora myszy w całym systemie")
    parser.add_argument('-q', '--quiet', action='store_true', help="Szybki podgląd tylko nazw kursorów (bez dodatkowych informacji)")
    parser.add_argument('-s', '--sizes', action='store_true', help="Wyświetla tylko informacje o rozmiarze kursorów")
    parser.add_argument('-n', '--names', action='store_true', help="Wyświetla tylko informacje o nazwach kursorów")
    
    args = parser.parse_args()
    quiet_mode = args.quiet
    show_names = args.names
    show_sizes = args.sizes

    if not show_names and not show_sizes:
        show_names = True
        show_sizes = True

    # Sprawdzenie plików i konfiguracji
    paths = [
        '/usr/share/icons/default/index.theme',
        os.path.expanduser('~/.icons/default/index.theme'),
        os.path.expanduser('~/.config/gtk-2.0/settings.ini'),
        os.path.expanduser('~/.config/gtk-3.0/settings.ini'),
        os.path.expanduser('~/.config/gtk-4.0/settings.ini'),
        os.path.expanduser('~/.config/kcminputrc'),
        os.path.expanduser('~/.config/kdedefaults/kcminputrc'),
        os.path.expanduser('~/.config/lxqt/lxqt.conf'),
        os.path.expanduser('~/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml'),
        os.path.expanduser('~/.config/xsettingsd/xsettingsd.conf')
    ]

    for path in paths:
        if 'gtk' in path:
            read_gtk_settings(path, quiet_mode, show_names, show_sizes)
        elif 'kcminputrc' in path:
            read_kde_settings(path, quiet_mode, show_names, show_sizes)
        elif 'lxqt.conf' in path:
            read_lxqt_settings(path, quiet_mode, show_names, show_sizes)
        elif 'xsettings' in path:
            read_xsettings(path, quiet_mode, show_names, show_sizes)
        else:
            read_index_theme(path, quiet_mode, show_names, show_sizes)

    # Sprawdzenie zmiennych środowiskowych
    check_environment_variables(quiet_mode, show_names, show_sizes)

    # Sprawdzenie ustawień dconf
    check_dconf(quiet_mode, show_names, show_sizes)

if __name__ == '__main__':
    main()
