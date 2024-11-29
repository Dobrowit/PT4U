#!/usr/bin/python3

import re
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox


class SnapManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Snap Manager")

        # Pole wyszukiwania
        search_frame = tk.Frame(root)
        search_frame.pack(fill=tk.X, pady=5)

        tk.Label(search_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_entry = tk.Entry(search_frame)
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.filter_entry.bind("<Return>", lambda event: self.refresh_data())  # Enter stosuje filtr

        # Tabela z listą pakietów
        self.tree = ttk.Treeview(root, columns=("Name", "Version", "Rev", "Tracking", "Publisher", "Notes"), show="headings")
        for col in ("Name", "Version", "Rev", "Tracking", "Publisher", "Notes"):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=150, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Przycisk panelu
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X)

        self.refreshlist_button = tk.Button(button_frame, text="Refresh list", command=self.refresh_data)
        self.refreshlist_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.info_button = tk.Button(button_frame, text="Info", command=self.show_info)
        self.info_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.remove_button = tk.Button(button_frame, text="Remove", command=self.remove_package)
        self.remove_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.refresh_button = tk.Button(button_frame, text="Refresh", command=self.refresh_package)
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.disable_button = tk.Button(button_frame, text="Disable", command=self.disable_package)
        self.disable_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.enable_button = tk.Button(button_frame, text="Enable", command=self.enable_package)
        self.enable_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.raw_data = []  # Pełna lista pakietów (do filtrowania)
        self.refresh_data()

    def execute_command_old(self, command):
        try:
            result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = result.communicate()

            if stderr:
                messagebox.showerror("Error", stderr)
            
            return stdout.strip() if not stderr else ""  # Jeśli jest błąd, nie zwracaj stdout

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Command failed: {e}")
            return ""

    def refresh_data(self):
        self.raw_data = []  # Opróżnij bufor danych
        # Pobierz dane z "snap list" tylko jeśli nie ma ich w buforze
        if not self.raw_data:
            output = self.execute_command("snap list")
            lines = output.splitlines()[1:]  # Skip header
            self.raw_data = [line.split() for line in lines]

        # Filtruj dane według pola wyszukiwania
        filter_text = self.filter_entry.get().lower()
        filtered_data = [
            parts for parts in self.raw_data
            if filter_text in parts[0].lower() or filter_text in parts[4].lower()
        ] if filter_text else self.raw_data

        # Oczyść tabelę i wypełnij ją przefiltrowanymi danymi
        self.tree.delete(*self.tree.get_children())
        for parts in filtered_data:
            notes = parts[-1] if len(parts) == 6 else ""
            publisher = parts[4] if len(parts) >= 5 else ""
            item = tuple(parts[:5]) + (notes,)

            # Określanie tagów na podstawie reguł
            tags = []
            if "disabled" in notes:
                tags.append("disabled")
            elif publisher.endswith("**"):
                tags.append("trusted")
            elif publisher.endswith("*"):
                if notes == "classic":
                    tags.append("classic_star")
                else:
                    tags.append("verified")
            elif notes == "classic":
                tags.append("classic_unverified")

            self.tree.insert("", tk.END, values=item, tags=tags)

        # Konfiguracja kolorów dla tagów
        self.tree.tag_configure("trusted", background="spring green")  # ** dwie gwiazdki
        self.tree.tag_configure("verified", background="pale green")  # * jedna gwiazdka
        self.tree.tag_configure("classic_star", background="yellow")  # * jedna gwiazdka i classic
        self.tree.tag_configure("classic_unverified", background="pink")  # brak gwiazdek i classic
        self.tree.tag_configure("disabled", background="deep sky blue")  # disabled

    
    def get_selected_package(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No package selected.")
            return None
        return self.tree.item(selected_item[0])["values"][0]
    
    def show_info_old(self):
        package = self.get_selected_package()
        if package:
            info = self.execute_command(f"snap info {package}")
            messagebox.showinfo("Package Info", info)

    def show_info(self):
        package = self.get_selected_package()
        if package:
            info = self.execute_command(f"snap info {package}")
            
            # Tworzymy nowe okno do wyświetlania informacji
            info_window = tk.Toplevel(self.root)
            info_window.title(f"Info: {package}")
            
            # Tworzymy kontrolkę Text i Scrollbar
            text_widget = tk.Text(info_window, wrap=tk.WORD, height=20, width=80)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = tk.Scrollbar(info_window, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            
            # Dodajemy tagi do URL
            url_pattern = r'https?://\S+'  # Regex do wykrywania URL (http lub https)
            
            # Funkcja do otwierania URL
            def open_url(event, url):
                subprocess.run(["xdg-open", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wstawiamy wynik polecenia do kontrolki Text i dodajemy tagi do URL
            text_widget.insert(tk.END, info)
            
            # Wyszukiwanie URL w tekście i dodawanie tagów do linków
            pos = '1.0'  # Początkowa pozycja w kontrolce Text
            url_counter = 1  # Licznik dla unikalnych tagów
            while True:
                # Szukamy URL w tekście
                match = re.search(url_pattern, text_widget.get(pos, 'end'))
                if not match:
                    break
                
                url = match.group(0)
                start_idx = text_widget.search(url, pos, stopindex='end')
                end_idx = f"{start_idx}+{len(url)}c"
                
                # Tworzymy unikalny tag dla każdego URL
                tag_name = f"url-{url_counter}"
                url_counter += 1
                
                # Dodajemy tag do URL
                text_widget.tag_add(tag_name, start_idx, end_idx)
                text_widget.tag_configure(tag_name, foreground="blue", underline=True)  # Ustawienie koloru i podkreślenia
                
                # Wiążemy kliknięcie na URL z otwarciem go w przeglądarce
                text_widget.tag_bind(tag_name, "<Button-1>", lambda event, url=url: open_url(event, url))
                
                # Zmieniamy kursor na rączkę
                text_widget.tag_bind(tag_name, "<Enter>", lambda event: text_widget.config(cursor="hand2"))
                text_widget.tag_bind(tag_name, "<Leave>", lambda event: text_widget.config(cursor=""))
                
                pos = end_idx  # Aktualizujemy pozycję do następnego URL-a
            
            text_widget.config(state=tk.DISABLED)  # Zablokowanie edycji tekstu

    def remove_package(self):
        package = self.get_selected_package()
        if package:
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove {package}?"):
                self.execute_command(f"snap remove {package}")
                self.refresh_data()
    
    def refresh_package(self):
        package = self.get_selected_package()
        command = f"snap refresh {package}" if package else "snap refresh"
        self.execute_command(command)
        self.refresh_data()
    
    def disable_package(self):
        package = self.get_selected_package()
        if package:
            self.execute_command(f"snap disable {package}")
            self.refresh_data()
    
    def enable_package(self):
        package = self.get_selected_package()
        if package:
            self.execute_command(f"snap enable {package}")
            self.refresh_data()
    
    def sort_column(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        data.sort(reverse=reverse)
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))


if __name__ == "__main__":
    root = tk.Tk()
    app = SnapManagerApp(root)
    root.mainloop()
