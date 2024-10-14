#!/usr/bin/python3

import os, subprocess

RED    = "\033[0;31m"
YELLOW = "\033[1;33m"
WHITE  = "\033[1;37m"
GREEN  = "\033[0;32m"
BLUE   = "\033[0;34m"
RESET  = "\033[0m"

def check_file_exists(file_path):
    if os.path.isfile(file_path):
        return True
    else:
        print(f"{RED}Brak pliku konfiguracyjnego!{RESET}")
        return False

def read_config(file_path, opt_name, sub_typ=1): # Typ 1
    print(f"{BLUE}{file_path}{RESET}")
    if check_file_exists(file_path):
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if opt_name in line:
                        match sub_typ:
                            case 1: print(f"Motyw kursora:{YELLOW}", line.split('=')[1].strip(), RESET)
                            case 2: print(f"Motyw kursora:{YELLOW}", line.split('value="')[1].split('"')[0], RESET)
                            case 3: print(f"Motyw kursora:{YELLOW}", line.split(' ', 1)[1].strip().strip('"'), RESET)
        except Exception as e:
            print(f"{RED}Nie udało się odczytać ustawień: {e}{RESET}")

def check_dconf(opt_name): # Typ 2
    print(f"{BLUE}{opt_name}{RESET}")
    try:
        cursor_name = subprocess.check_output(['dconf', 'read', opt_name]).decode().strip().strip("'")
        print(f"Motyw kursora: {YELLOW}{cursor_name}{RESET}")
    except Exception as e:
        print(f"{RED}Nie udało się odczytać ustawień: {e}{RESET}")

def check_env_var(env_var): # Typ 3
    print(f"{BLUE}{env_var}{RESET}")
    try:
        cursor_name = os.getenv(env_var)
        if cursor_name:
            print(f"Motyw kursora: {YELLOW}{cursor_name}{RESET}")
        else:
            print(f"{RED}Brak zmiennej {env_var}!{RESET}")
    except Exception as e:
        print(f"{RED}Nie udało się odczytać ustawień: {e}{RESET}")
    
# Słownik paths z typami i nazwami konfiguracji
paths = {
                  "Default": [1, '/usr/share/icons/default/index.theme', 'Name', 1],
             "User default": [1, '~/.icons/default/index.theme', 'Name', 1],
               "xsettingsd": [1, '~/.config/xsettingsd/xsettingsd.conf', 'Gtk/CursorThemeName', 3],
                     "GTK2": [1, '~/.config/gtk-2.0/settings.ini', 'gtk-cursor-theme-name', 1],
                     "GTK3": [1, '~/.config/gtk-3.0/settings.ini', 'gtk-cursor-theme-name', 1],
                     "GTK4": [1, '~/.config/gtk-4.0/settings.ini', 'gtk-cursor-theme-name', 1],
                      "KDE": [1, '~/.config/kcminputrc', 'cursorTheme', 1],
              "KDE default": [1, '~/.config/kdedefaults/kcminputrc', 'cursorTheme', 1],
                     "LXQT": [1, '~/.config/lxqt/lxqt.conf', 'icon_theme', 1],
                    "XFCE4": [1, '~/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml', 'CursorThemeName', 2],
                    "GNOME": [2, '', '/org/gnome/desktop/interface/cursor-theme', 0],
                     "MATE": [2, '', '/org/mate/desktop/peripherals/mouse/cursor-theme', 0],                    
                      "X11": [3, '', 'XCURSOR_THEME', 0]
}

for name, (config_type, path, opt_name, sub_typ) in paths.items():
    full_path = os.path.expanduser(path)
    print(f"\n{name} ({GREEN}{opt_name}{RESET}): ", end='')
    match config_type:
        case 1: read_config(full_path, opt_name, sub_typ)
        case 2: check_dconf(opt_name)
        case 3: check_env_var(opt_name)

