#!/usr/bin/python3
# Konweryje pliki .desktop do menu Fluxbox

import os
import configparser
import re
import random
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

# Stałe do konfiguracji skryptu
MENU_PATH = os.path.expanduser("~/.fluxbox/menu")  # Ścieżka do generowanego menu
SYSMENU = True  # Dodaje końcowe menu
SORT = True  # Sortuje wszystkie pozycje
SORTCATEGORY = True  # Sortuje kategorie alfabetycznie
COMMENT = True  # Dodaje opisy
CHNAME = 1  # 0: bez zmian, 1: małe, 2: duże, 3: pierwsza duża, 4: każdy wyraz duży, 5: losowo
TRUENAME = True  # Używa nazwy polecenia z Exec zamiast nazwy z Name
TOCON = False  # Jeśli True, konfiguracja będzie wyświetlana na ekranie, a nie zapisywana do pliku
MAX_COMMENT_LENGTH = 22  # Maksymalna długość opisu
COMPACT = True  # Jeśli True, pomija określone kategorie
DEFAULT_TERMINAL = "gnome-terminal"  # Domyślny terminal

# Funkcja do wyszukiwania dostępnych terminali
def find_installed_terminals():
    known_terminals = [
        "xterm",
        "gnome-terminal",
        "terminology",
        "konsole",
        "lxterminal",
        "tilix",
        "terminator",
        "kitty",
        "alacritty",
        "xfce4-terminal",
        "cool-retro-term"
    ]

    installed_terminals = []

    for terminal in known_terminals:
        if is_terminal_installed(terminal):
            installed_terminals.append(terminal)

    return installed_terminals

# Funkcja do sprawdzania, czy terminal jest zainstalowany
def is_terminal_installed(terminal):
    try:
        subprocess.run(["which", terminal], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# Funkcja do generowania menu Fluxbox na podstawie ustawień
def generate_menu():
    global menu_item_count  # Deklaracja globalnej zmiennej
    menu_item_count = 0  # Inicjalizacja licznika pozycji menu

    # Ustawienia z GUI
    menu_path = menu_path_entry.get()
    sysmenu = sysmenu_var.get()
    sort_option = sort_var.get()
    comment_option = comment_var.get()
    max_comment_length = int(max_comment_length_entry.get())
    chname_option = chname_combobox.get()
    truename = truename_var.get()
    tocon = tocon_var.get()
    compact = compact_var.get()
    terminal_command = terminal_combobox.get()  # Odczytujemy wybrany terminal
    sort_category = sort_category_var.get()  # Odczytujemy opcję sortowania kategorii

    # Słownik kategorii, które posłużą jako główne podmenu
    categories = {}

    # Funkcja do parsowania plików .desktop
    def parse_desktop_file(file_path):
        config = configparser.ConfigParser(interpolation=None)
        config.read(file_path)
        if 'Desktop Entry' in config:
            entry = config['Desktop Entry']
            no_display = entry.get('NoDisplay', 'false').lower() == 'true'
            if no_display:
                return None, None, None, None  # Pomijamy, jeśli NoDisplay=true
            name = entry.get('Name', None)
            exec_cmd = entry.get('Exec', None)
            category = entry.get('Categories', None)
            terminal = entry.get('Terminal', 'false').lower() == 'true'  # Sprawdzanie pola Terminal

            # Pobieranie opisu z Comment[pl] lub Comment
            comment = entry.get('Comment[pl]', entry.get('Comment', None))

            # Skracanie opisu, jeśli przekracza limit znaków
            if comment_option and comment and len(comment) > max_comment_length:
                comment = comment[:max_comment_length].strip() + '...'

            # Użycie exec_cmd jako nazwy, jeśli TRUENAME jest ustawione na True
            if truename:
                exec_cmd_cleaned = exec_cmd.replace('"', '').strip()  # Usuwa cudzysłowy
                name = os.path.basename(exec_cmd_cleaned.split()[0])  # Używa tylko pierwszej części polecenia

            # Usuwanie zmiennych z polecenia Exec
            if exec_cmd:
                exec_cmd = re.sub(r'%[fuFUdDnNiIcCmMsS]', '', exec_cmd).strip()

            # Pobieranie kategorii jako listy
            if category:
                #category_list = category.split(';')  # Rozdzielamy kategorie
                category_list = [cat for cat in category.split(';') if cat]
            else:
                category_list = []

            # Jeśli terminal=true, przypisujemy kategorię ConsoleOnly
            if terminal:
                category = "ConsoleOnly"
                exec_cmd = f"{terminal_command} -e {exec_cmd}"  # Uruchamiamy w wybranym terminalu
                return name, exec_cmd, category, comment

            # Pomijanie określonych kategorii
            if compact:
                filtered_categories = [cat for cat in category_list if cat not in ["GNOME", "GTK", "KDE", "Qt", "Core", "Settings", "DesktopSettings", "Documentation", "System", "HardwareSettings"] and not cat.startswith("X-")]
                if filtered_categories:
                    category = filtered_categories[0]  # Używamy pierwszej dostępnej kategorii
                else:
                    category = "Inne"  # Brak kategorii
                return name, exec_cmd, category, comment
            else:
                if category_list:
                    category = category_list[0]  # Używamy pierwszej dostępnej kategorii
                else:
                    category = "Inne"  # Brak kategorii
                return name, exec_cmd, category, comment

        return None, None, None, None

    # Funkcja do zmiany wielkości liter w nazwach
    def change_case(name):
        if chname_option == "Małe":
            return name.lower()
        elif chname_option == "Duże":
            return name.upper()
        elif chname_option == "Pierwsza duża":
            return name.capitalize()
        elif chname_option == "Każdy wyraz duży":
            return name.title()
        elif chname_option == "Losowo":
            return ''.join(random.choice([c.lower(), c.upper()]) for c in name)
        return name  # bez zmian

    # Przeszukiwanie katalogów
    desktop_dirs = [
        "/usr/share/applications",
        "/var/lib/snapd/desktop/applications",
        os.path.expanduser("~/.local/share/applications")
    ]

    for directory in desktop_dirs:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.endswith(".desktop"):
                    filepath = os.path.join(directory, filename)
                    name, exec_cmd, category, comment = parse_desktop_file(filepath)

                    if name and exec_cmd and category:
                        # Zmiana wielkości liter w nazwie
                        name = change_case(name)

                        if category not in categories:
                            categories[category] = []

                        # Dodajemy aplikację do odpowiedniej kategorii z opisem (jeśli jest)
                        full_name = f"{name} - {comment}" if comment_option and comment else name
                        categories[category].append((full_name, exec_cmd))
                        menu_item_count += 1  # Zwiększamy licznik pozycji menu

    # Sortowanie aplikacji w każdej kategorii
    if sort_option:
        for cat in categories:
            categories[cat].sort(key=lambda x: x[0].lower())  # Sortowanie wg nazwy

    # Sortowanie kategorii, jeśli wybrano sortowanie
    if sort_category:
        #sorted_categories = sorted(categories.keys())  # Sortowanie kluczy słownika (nazw kategorii)
        #sorted_categories = {klucz: categories[klucz] for klucz in sorted(categories)}
        sorted_categories = sorted(categories)
    else:
        #sorted_categories = categories.keys()  # Używamy kategorii bez sortowania
        sorted_categories = categories.keys()

    # Generowanie menu Fluxbox
    if tocon:
        # Wyświetlanie na ekranie zamiast zapisywania do pliku
        print("[begin] (Fluxbox Menu)")
        for category in sorted_categories:
            apps = categories[category]
            if apps:
                print(f"  [submenu] ({category})")
                for name, exec_cmd in apps:
                    print(f"    [exec] ({name}) {{{exec_cmd}}}")
                print("  [end]")
        
        if sysmenu:
            print("  [separator]")
            print("  [config] (Configuration)")
            print("  [submenu] (Styles) {}")
            print("    [stylesdir] (/usr/share/fluxbox/styles)")
            print("    [stylesdir] (~/.fluxbox/styles)")
            print("  [end]")
            print("  [workspaces] (Workspaces)")
            print("  [reconfig] (Reconfigure)")
            print("  [restart] (Restart)")
            print("  [exit] (Exit)")
        print("[end]")
    else:
        # Zapisywanie do pliku menu
        with open(menu_path, 'w') as f:
            f.write("[begin] (Fluxbox Menu)\n")
            for category in sorted_categories:
                apps = categories[category]
                if apps:
                    f.write(f"  [submenu] ({category})\n")
                    for name, exec_cmd in apps:
                        f.write(f"    [exec] ({name}) {{{exec_cmd}}}\n")
                    f.write("  [end]\n")
            
            # Dodawanie opcji konfiguracyjnych na końcu menu
            if sysmenu:
                f.write("  [separator]\n")  # Zachowano tylko pierwszy separator
                f.write("  [config] (Configuration)\n")
                f.write("  [submenu] (Styles) {}\n")
                f.write("    [stylesdir] (/usr/share/fluxbox/styles)\n")
                f.write("    [stylesdir] (~/.fluxbox/styles)\n")
                f.write("  [end]\n")
                f.write("  [workspaces] (Workspaces)\n")
                f.write("  [reconfig] (Reconfigure)\n")
                f.write("  [restart] (Restart)\n")
                f.write("  [exit] (Exit)\n")

            f.write("[end]\n")

    # Wyświetlenie liczby dodanych pozycji
    messagebox.showinfo("Sukces", f"Menu Fluxbox wygenerowane pomyślnie!\nDodano {menu_item_count} pozycji menu.")

# Wyszukiwanie zainstalowanych terminali
installed_terminals = find_installed_terminals()

# Tworzenie głównego okna
root = tk.Tk()
root.title("Generator Menu Fluxbox")

# Kontrolki do ustawiania stałych
tk.Label(root, text="Ścieżka do menu:").grid(row=0, column=0, sticky=tk.W)
menu_path_entry = tk.Entry(root, width=40)
menu_path_entry.grid(row=0, column=1, padx=5, pady=5)
menu_path_entry.insert(0, MENU_PATH)  # Ustaw domyślną wartość

tk.Label(root, text="Maks. długość opisu:").grid(row=1, column=0, sticky=tk.W)
max_comment_length_entry = tk.Entry(root, width=5)
max_comment_length_entry.grid(row=1, column=1, padx=5, pady=5)
max_comment_length_entry.insert(0, str(MAX_COMMENT_LENGTH))  # Ustaw domyślną wartość

tk.Label(root, text="Zmiana wielkości liter:").grid(row=2, column=0, sticky=tk.W)
chname_combobox = ttk.Combobox(root, values=["Bez zmian", "Małe", "Duże", "Pierwsza duża", "Każdy wyraz duży", "Losowo"])
chname_combobox.grid(row=2, column=1, padx=5, pady=5)
chname_combobox.set(["Bez zmian", "Małe", "Duże", "Pierwsza duża", "Każdy wyraz duży", "Losowo"][CHNAME])  # Ustaw domyślną wartość

sysmenu_var = tk.BooleanVar(value=SYSMENU)
tk.Checkbutton(root, text="Dodaj końcowe menu", variable=sysmenu_var).grid(row=3, column=0, columnspan=2, sticky=tk.W)

sort_var = tk.BooleanVar(value=SORT)
tk.Checkbutton(root, text="Sortuj pozycje", variable=sort_var).grid(row=4, column=0, columnspan=2, sticky=tk.W)

comment_var = tk.BooleanVar(value=COMMENT)
tk.Checkbutton(root, text="Dodaj opisy", variable=comment_var).grid(row=5, column=0, columnspan=2, sticky=tk.W)

truename_var = tk.BooleanVar(value=TRUENAME)
tk.Checkbutton(root, text="Użyj nazwy polecenia z Exec", variable=truename_var).grid(row=6, column=0, columnspan=2, sticky=tk.W)

tocon_var = tk.BooleanVar(value=TOCON)
tk.Checkbutton(root, text="Wyświetl na ekranie", variable=tocon_var).grid(row=7, column=0, columnspan=2, sticky=tk.W)

compact_var = tk.BooleanVar(value=COMPACT)
tk.Checkbutton(root, text="Pomijaj kategorie GNOME, GTK, KDE, Qt, X-XFCE", variable=compact_var).grid(row=8, column=0, columnspan=2, sticky=tk.W)

sort_category_var = tk.BooleanVar(value=SORTCATEGORY)
tk.Checkbutton(root, text="Sortuj kategorie", variable=sort_category_var).grid(row=9, column=0, columnspan=2, sticky=tk.W)

# Kontrolka do wyboru domyślnego terminala
tk.Label(root, text="Wybierz terminal:").grid(row=10, column=0, sticky=tk.W)
terminal_combobox = ttk.Combobox(root, values=installed_terminals)
terminal_combobox.grid(row=10, column=1, padx=5, pady=5)
terminal_combobox.set(DEFAULT_TERMINAL)  # Ustaw domyślną wartość

# Przycisk do generowania menu
generate_button = tk.Button(root, text="Generuj Menu", command=generate_menu)
generate_button.grid(row=11, column=0, columnspan=2, pady=11)

root.mainloop()
