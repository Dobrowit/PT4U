#!/usr/bin/python3

import os
import argparse
import configparser
import subprocess
import glob
import apt
import shutil
import cairosvg
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor, as_completed

domyslny_katalog = '/usr/share/applications/'
my_padx=5
table_data = []
info_window = None

# Funkcja do szukania plików .desktop
def find_desktop_files(directory):
    desktop_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".desktop"):
                desktop_files.append(os.path.join(root, file))
    return desktop_files

# Sprawdzenie pliku binarnego
def check_libraries(exec_path):
    try:
        output = subprocess.check_output(['ldd', exec_path], stderr=subprocess.DEVNULL).decode()
        if 'libgtk' in output.lower():
            return 'GTK'
        elif 'libqt' in output.lower() or 'libQt' in output:
            return 'QT'
    except Exception as e:
        #print(f"Error checking libraries for {exec_path}: {e}")
        pass
    return 'INNE'

# Funkcja do pobierania nazwy programu z pliku .desktop
def get_program_name(desktop_file):
    config = configparser.ConfigParser()
    config.read(desktop_file, encoding='utf-8')

    if 'Desktop Entry' in config and 'Name' in config['Desktop Entry']:
        return config['Desktop Entry']['Name']
    return None

# Funkcja do sprawdzania, do jakiego pakietu .deb należy dany plik
def find_deb_package(desktop_file):
    try:
        result = subprocess.run(['dpkg', '-S', desktop_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split(':')[0]  # Tylko nazwa pakietu przed dwukropkiem
        else:
            return "Nie znaleziono pakietu"
    except Exception as e:
        return f"Błąd: {str(e)}"

# Funkcja do wyciągania nazwy środowiska
def get_environment(desktop_file):
    config = configparser.ConfigParser(interpolation=None, strict=False)
    config.read(desktop_file, encoding='utf-8')

    # Sybkie sprawdzenie po nazwie pliku .desktop
    if 'kde.' in os.path.basename(desktop_file).lower():
        return 'KDE'
    if 'gnome.' in os.path.basename(desktop_file).lower():
        return 'GNOME'

    # Sprawdzanie na podstawie znanych kategorii w pliku .desktop
    if 'Desktop Entry' in config and 'Categories' in config['Desktop Entry']:
        categories = config['Desktop Entry']['Categories']
        if 'KDE' in categories:
            return 'KDE'
        elif 'GNOME' in categories:
            return 'GNOME'
        elif 'Qt' in categories:
            return 'QT'
        elif 'GTK' in categories:
            return 'GTK'
        elif 'ConsoleOnly' in categories or 'Terminal' in categories:
            return 'KONSOLA'

    # Jeśli po powyższe zawiodło to szukaj nazw bibliotek w głównym pliku wykonywalnym
    try:
        exec_command = config['Desktop Entry']['Exec'].split()[0].replace('%', '')  # Usunięcie parametrów
        exec_path = shutil.which(exec_command)
        if exec_path:
            return check_libraries(exec_path)
    except Exception as e:
        #print(f"Error checking libraries: {e}")
        pass

    return 'INNE'

# Funkcja do odczytu informacji o pakiecie
def get_package_info(package_name):
    cache = apt.Cache()
    if package_name in cache:
        pkg = cache[package_name]

        if not pkg.versions:
            return "Brak informacji o wersji"

        # Pobieranie podstawowych informacji
        version = pkg.versions[0].version
        description = pkg.versions[0].description
        dependencies = pkg.versions[0].dependencies

        # Formatowanie zależności do tekstu
        deps_text = ", ".join([str(dep[0].name) for dep in dependencies]) if dependencies else "Brak zależności"

        # Tworzenie pełnego opisu
        full_info = (
            f"{description}\n\n"
            f"Wersja:\n{version}\n\n"
            f"Zależności:\n{deps_text}"
        )
        return full_info
    return "Nie znaleziono pakietu"

# Funkcja do odczytu informacji o pakiecie
def get_package_info_old(package_name):
    cache = apt.Cache()
    if package_name in cache:
        pkg = cache[package_name]
        description = pkg.versions[0].description if pkg.versions else "Brak opisu"
        return description
    return "Nie znaleziono pakietu"

# Funkcja do pobrania ikony pakietu
def get_package_icon(icon_name):
    icon_dirs = [
        "/usr/share/icons/Yaru",
        "/usr/share/icons/Humanity",
        "/usr/share/icons/hicolor",
        "/usr/share/icons/Papirus",
        "/usr/share/icons/breeze",
        "/usr/share/icons/elementary",
        "/usr/share/icons/oxygen",
        "/usr/share/pixmaps"
    ]

    for dir in icon_dirs:
        for ext in ['.png', '.svg']:
            for size in ['48x48', '48']:
                icon_path = Path(dir) / f"{size}/apps/{icon_name}{ext}"
                if icon_path.exists():
                    if ext == '.svg':
                        png_path = "/tmp/temp_icon.png"
                        cairosvg.svg2png(url=str(icon_path), write_to=png_path)
                        return Image.open(png_path)
                    else:
                        return Image.open(icon_path)

    # Jeśli nie znaleziono żadnej ikony, zwracamy None
    return None

def get_package_icon_old(icon_name):
    # Wzorce do wyszukiwania ikon w różnych lokalizacjach
    search_patterns = [
        f"/usr/share/icons/Yaru/48x48/apps/{icon_name}.png",
        f"/usr/share/icons/Yaru/48x48/apps/{icon_name}.svg",
        f"/usr/share/icons/Humanity/48/apps/{icon_name}.png",
        f"/usr/share/icons/Humanity/48/apps/{icon_name}.svg",
        f"/usr/share/icons/hicolor/48x48/apps/{icon_name}.png",
        f"/usr/share/icons/hicolor/48x48/apps/{icon_name}.svg",
        f"/usr/share/icons/Papirus/48x48/apps/{icon_name}.png",
        f"/usr/share/icons/Papirus/48x48/apps/{icon_name}.svg",
        f"/usr/share/icons/breeze/apps/48/{icon_name}.png",
        f"/usr/share/icons/breeze/apps/48/{icon_name}.svg",
        f"/usr/share/icons/elementary/48/apps/{icon_name}.png",
        f"/usr/share/icons/elementary/48/apps/{icon_name}.svg",
        f"/usr/share/icons/oxygen/48x48/apps{icon_name}.png",
        f"/usr/share/icons/oxygen/48x48/apps{icon_name}.svg",
        f"/usr/share/pixmaps/{icon_name}.png",
        f"/usr/share/pixmaps/{icon_name}.svg"
    ]

    for pattern in search_patterns:
        print(pattern)
        icon_paths = glob.glob(pattern)
        if icon_paths:
            icon_path = icon_paths[0]
            print("Znaleziono! - ", icon_path)
            # Obsługa plików .svg
            if icon_path.lower().endswith('.svg'):
                # Konwersja SVG na PNG
                png_path = "/tmp/temp_icon.png"
                cairosvg.svg2png(url=icon_path, write_to=png_path)
                return Image.open(png_path)
            else:
                # Obsługa innych formatów obsługiwanych przez Pillow
                return Image.open(icon_path)

    # Jeśli nie znaleziono żadnej ikony, zwracamy None
    return None

# Funkcja do odinstalowania pakietu
def uninstall_package(package_name):
    global table_data
    try:
        subprocess.run(['sudo', 'apt', 'remove', package_name], check=True)
        messagebox.showinfo("Sukces", f"Pakiet {package_name} został odinstalowany.")
        # Po pomyślnym usunięciu, usuń wiersz z tabeli
        remove_row_by_package_name(package_name)
    except subprocess.CalledProcessError:
        messagebox.showerror("Błąd", f"Nie udało się odinstalować pakietu {package_name}.")

# Funkcja do kasowania pliku .desktop
def del_desktop(desktop_name):
    global table_data
    try:
        subprocess.run(['rm', '-f', domyslny_katalog+desktop_name], check=True)
        messagebox.showinfo("Sukces", f"Plik {desktop_name} został skasowany.")
        remove_row_by_package_name2(desktop_name)
    except subprocess.CalledProcessError:
        messagebox.showerror("Błąd", f"Nie udało się skasować {desktop_name}.")


# Usuwanie wiersza po nazwie pakietu deb
def remove_row_by_package_name(package_name):
    # Iterowanie przez wszystkie wiersze w Treeview
    for item in tree.get_children():
        # Sprawdzenie, czy wartość w kolumnie "Pakiet deb" (druga kolumna) pasuje do podanej nazwy pakietu
        if tree.item(item)['values'][1] == package_name:
            # Usunięcie wiersza
            tree.delete(item)
            break  # Jeśli chcesz usunąć tylko pierwszy znaleziony wiersz, zakończ pętlę

def remove_row_by_package_name2(package_name):
    # Iterowanie przez wszystkie wiersze w Treeview
    for item in tree.get_children():
        # Sprawdzenie, czy wartość w kolumnie "Pakiet deb" (druga kolumna) pasuje do podanej nazwy pakietu
        if tree.item(item)['values'][2] == package_name:
            # Usunięcie wiersza
            tree.delete(item)
            break  # Jeśli chcesz usunąć tylko pierwszy znaleziony wiersz, zakończ pętlę

# Funkcja do wyświetlenia szczegółów o pakiecie
def show_more_info(package_name):
    global info_window
    description = get_package_info(package_name)
    icon = get_package_icon(package_name)

    if info_window is None or not info_window.winfo_exists():
        info_window = tk.Toplevel(root)
        info_window.title(f"Informacje o pakiecie {package_name}")

        if icon:
            img = ImageTk.PhotoImage(icon)
            icon_label = tk.Label(info_window, image=img)
            icon_label.image = img
            icon_label.pack()

        description_label = tk.Label(info_window, text=description, wraplength=600)
        description_label.pack()
        close_button = tk.Button(info_window, text="Zamknij", command=close_info_window)
        close_button.pack(pady=10)
        info_window.protocol("WM_DELETE_WINDOW", close_info_window)
        info_window.bind("<Escape>", close_info)


# Funkcja dla podwójnego kliknięcia lub przycisku "Więcej informacji"
def on_double_click(event):
    selected_item = tree.focus()
    if selected_item:
        package_name = tree.item(selected_item)['values'][1]
        show_more_info(package_name)

# Funkcja do sortowania kolumn
def sort_column(col, reverse):
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    data.sort(reverse=reverse)

    for index, (val, item) in enumerate(data):
        tree.move(item, '', index)

    tree.heading(col, command=lambda: sort_column(col, not reverse))

from concurrent.futures import ThreadPoolExecutor, as_completed

def process_desktop_file(desktop_file):
    program_name = get_program_name(desktop_file)
    if program_name:
        package_name = find_deb_package(desktop_file)
        desktop_filename = os.path.basename(desktop_file)  # Tylko nazwa pliku .desktop
        environment = get_environment(desktop_file)  # Środowisko
        tag = "nie_znaleziono" if package_name == "Nie znaleziono pakietu" else ""
        return (program_name, package_name, desktop_filename, environment, tag)
    return None

def close_info_window():
    global info_window
    if info_window is not None:
        info_window.destroy()
        info_window = None

def close_info(event):
    close_info_window()

# Funkcja do przetwarzania plików .desktop z paskiem postępu
def main(directory, turbo=False):
    global table_data
    desktop_files = find_desktop_files(directory)
    total_files = len(desktop_files)

    if total_files == 0:
        messagebox.showinfo("Informacja", "Nie znaleziono plików .desktop")
        return

    # Konfiguracja paska postępu
    progress_bar["maximum"] = total_files

    if turbo:
        start_time = time.time()

        results = []

        with ThreadPoolExecutor() as executor:
            # Zlecanie zadań do wykonania
            future_to_file = {executor.submit(process_desktop_file, desktop_file): desktop_file for desktop_file in desktop_files}

            for index, future in enumerate(as_completed(future_to_file)):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    # Obsługa błędów
                    print(f"Błąd przetwarzania pliku {future_to_file[future]}: {e}")

                # Aktualizacja paska postępu
                progress_bar["value"] = index + 1
                progress_bar.update()

        # Wstawianie wyników do drzewa
        for result in results:
            program_name, package_name, desktop_filename, environment = result[:4]
            tag = "no_deb" if package_name == "Nie znaleziono pakietu" else ""
            tree.insert("", "end", values=(program_name, package_name, desktop_filename, environment), tags=(tag,))
#            tree.insert("", "end", values=result)

        execution_time = time.time() - start_time
        print(f"Czas wykonywania skanowania: {execution_time:.2f} sekund")
    else:
        start_time = time.time()

        for index, desktop_file in enumerate(desktop_files):
            try:
                program_name = get_program_name(desktop_file)
                if program_name:
                    package_name = find_deb_package(desktop_file)
                    desktop_filename = os.path.basename(desktop_file)  # Tylko nazwa pliku .desktop
                    environment = get_environment(desktop_file)  # Środowisko

                    tag = "nie_znaleziono" if package_name == "Nie znaleziono pakietu" else ""
                    tree.insert("", "end", values=(program_name, package_name, desktop_filename, environment), tags=(tag,))   
            except:
                pass

            # Aktualizacja paska postępu
            progress_bar["value"] = index + 1
            progress_bar.update()

        execution_time = time.time() - start_time
        print(f"Czas wykonywania skanowania: {execution_time:.2f} sekund")

def show_context_menu(event):
    # Wyświetlanie menu kontekstowego
    menu.tk_popup(event.x_root, event.y_root)

def option1():
    selected = tree.curselection()
    if selected:
        item = tree.get(selected)
        print(f"Wybrano: {item} - Opcja 1")

def option2():
    selected = tree.curselection()
    if selected:
        item = tree.get(selected)
        print(f"Wybrano: {item} - Opcja 2")

# Pobieranie opcji z linii poleceń
parser = argparse.ArgumentParser(description="Ta aplikacja szuka plików .desktop i sprawdza czy działają oraz sprawdza do jakiego pakietu deb należy.")

parser.add_argument('--turbo', action='store_true', help="Aktywuje tryb turbo - procesowanie wielowątkowe")
parser.add_argument('--dir', type=str, help=f"Ścieżka do skanoanego katalogu. Domyślnie jest {domyslny_katalog}")
parser.add_argument('--padx', type=str, help=f"Ustala odstępy pomiędzy kontrolkami. Domyślnie jest {my_padx}")

args = parser.parse_args()

domyslny_katalog = args.dir if args.dir else domyslny_katalog
my_padx = args.padx if args.padx else my_padx

# Tworzenie GUI
root = tk.Tk()
root.title("Menadżer plików .desktop")
root.geometry("850x500")

# Dodanie paska przewijania
scrollbar = tk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Tworzenie drzewa z kolumnami
columns = ("Program", "Pakiet deb", "Plik .desktop", "Środowisko")
tree = ttk.Treeview(root, columns=columns, show="headings", yscrollcommand=scrollbar.set)
tree.heading("Program", text="Program", command=lambda: sort_column("Program", False))
tree.heading("Pakiet deb", text="Pakiet deb", command=lambda: sort_column("Pakiet deb", False))
tree.heading("Plik .desktop", text="Plik .desktop", command=lambda: sort_column("Plik .desktop", False))
tree.heading("Środowisko", text="Środowisko", command=lambda: sort_column("Środowisko", False))
tree.tag_configure("no_deb", background="red")
tree.pack(fill=tk.BOTH, expand=True)

# Tworzenie ramki dla paska postępu i przycisków
controls_frame = tk.Frame(root)
controls_frame.pack(fill=tk.X, pady=my_padx)

# Konfiguracja paska przewijania
scrollbar.config(command=tree.yview)

# Podwójne kliknięcie wyświetla informacje o pakiecie
tree.bind("<Double-1>", on_double_click)

# Tworzenie paska postępu
progress_bar = ttk.Progressbar(controls_frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=my_padx)

# Dodanie przycisków do tej samej ramki
info_button = tk.Button(controls_frame, text="Więcej informacji", command=lambda: on_double_click(None))
info_button.pack(side=tk.LEFT, padx=my_padx)

uninstall_button = tk.Button(controls_frame, text="Odinstaluj", command=lambda: uninstall_package(tree.item(tree.focus())['values'][1]))
uninstall_button.pack(side=tk.LEFT, padx=my_padx)

del_button = tk.Button(controls_frame, text="Skasuj plik .desktop", command=lambda: del_desktop(tree.item(tree.focus())['values'][2]))
del_button.pack(side=tk.LEFT, padx=my_padx)

# Tworzenie menu kontekstowego
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Opcja 1", command=option1)
menu.add_command(label="Opcja 2", command=option2)

# Przypisanie menu kontekstowego do tabeli
tree.bind("<Button-3>", show_context_menu)

# Uruchomienie głównej funkcji
if args.turbo:
    main(domyslny_katalog, True)
else:
    main(domyslny_katalog, False)

# Uruchomienie GUI
root.mainloop()
