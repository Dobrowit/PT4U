#!/usr/bin/python3

import re
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox

class SnapManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Snap Manager")

        search_frame = tk.Frame(root)
        search_frame.pack(fill=tk.X, pady=5)

        tk.Label(search_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        self.filter_entry = tk.Entry(search_frame)
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.filter_entry.bind("<Return>", lambda event: self.refresh_data())

        self.tree = ttk.Treeview(root, columns=("Name", "Version", "Rev", "Tracking", "Publisher", "Notes"), show="headings")
        for col in ("Name", "Version", "Rev", "Tracking", "Publisher", "Notes"):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=150, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X)

        self.refreshlist_button = tk.Button(button_frame, text="Refresh list", command=self.refresh_data)
        self.refreshlist_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.info_button = tk.Button(button_frame, text="Info", command=lambda: self.show_info(self.tree))
        self.info_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.remove_button = tk.Button(button_frame, text="Remove", command=lambda: self.remove_package(self.tree))
        self.remove_button.pack(side=tk.LEFT, padx=5, pady=5)
                
        self.refresh_button = tk.Button(button_frame, text="Refresh", command=lambda: self.refresh_package(self.tree))
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.disable_button = tk.Button(button_frame, text="Disable", command=lambda: self.disable_package(self.tree))
        self.disable_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.enable_button = tk.Button(button_frame, text="Enable", command=lambda: self.enable_package(self.tree))
        self.enable_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.services_button = tk.Button(button_frame, text="Services", command=self.show_services)
        self.services_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.snap_install_button = tk.Button(button_frame, text="Snap Install", command=self.open_snap_install)
        self.snap_install_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.raw_data = []
        self.refresh_data()

    def refresh_data(self):
        self.raw_data = []
        if not self.raw_data: # Pobierz dane z "snap list" tylko jeśli nie ma ich w buforze
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

        self.tree.tag_configure("trusted", background="spring green")  # ** dwie gwiazdki
        self.tree.tag_configure("verified", background="pale green")  # * jedna gwiazdka
        self.tree.tag_configure("classic_star", background="yellow")  # * jedna gwiazdka i classic
        self.tree.tag_configure("classic_unverified", background="pink")  # brak gwiazdek i classic
        self.tree.tag_configure("disabled", background="deep sky blue")  # disabled

    def show_services(self):
        info = self.execute_command(f"snap services")
        info_window = tk.Toplevel(self.root)
        info_window.title(f"Services")
        info_window.transient(self.root)
        info_window.grab_set() 
        text_widget = tk.Text(info_window, wrap=tk.WORD, height=20, width=80)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = tk.Scrollbar(info_window, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.insert(tk.END, info)
        
        # Wyszukiwanie URL w tekście i dodawanie tagów do linków
        pos = '1.0'
        url_counter = 1
        url_pattern = r'https?://\S+'
        while True:
            match = re.search(url_pattern, text_widget.get(pos, 'end'))
            if not match:
                break
            url = match.group(0)
            start_idx = text_widget.search(url, pos, stopindex='end')
            end_idx = f"{start_idx}+{len(url)}c"
            tag_name = f"url-{url_counter}"
            url_counter += 1
            text_widget.tag_add(tag_name, start_idx, end_idx)
            text_widget.tag_configure(tag_name, foreground="blue", underline=True)
            text_widget.tag_bind(tag_name, "<Button-1>", lambda event, url=url: open_url(event, url))
            text_widget.tag_bind(tag_name, "<Enter>", lambda event: text_widget.config(cursor="hand2"))
            text_widget.tag_bind(tag_name, "<Leave>", lambda event: text_widget.config(cursor=""))
            pos = end_idx
        text_widget.config(state=tk.DISABLED)


    def show_info(self, treeview):
        package = self.get_selected_package(treeview)
        if package:
            def open_url(event, url):
                subprocess.run(["xdg-open", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            info = self.execute_command(f"snap info {package}")
            info_window = tk.Toplevel(self.root)
            info_window.title(f"Info: {package}")
            info_window.transient(self.root)
            info_window.grab_set() 
            text_widget = tk.Text(info_window, wrap=tk.WORD, height=20, width=80)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar = tk.Scrollbar(info_window, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            text_widget.insert(tk.END, info)
            
            # Wyszukiwanie URL w tekście i dodawanie tagów do linków
            pos = '1.0'
            url_counter = 1
            url_pattern = r'https?://\S+'
            while True:
                match = re.search(url_pattern, text_widget.get(pos, 'end'))
                if not match:
                    break
                url = match.group(0)
                start_idx = text_widget.search(url, pos, stopindex='end')
                end_idx = f"{start_idx}+{len(url)}c"
                tag_name = f"url-{url_counter}"
                url_counter += 1
                text_widget.tag_add(tag_name, start_idx, end_idx)
                text_widget.tag_configure(tag_name, foreground="blue", underline=True)
                text_widget.tag_bind(tag_name, "<Button-1>", lambda event, url=url: open_url(event, url))
                text_widget.tag_bind(tag_name, "<Enter>", lambda event: text_widget.config(cursor="hand2"))
                text_widget.tag_bind(tag_name, "<Leave>", lambda event: text_widget.config(cursor=""))
                pos = end_idx
            text_widget.config(state=tk.DISABLED)

    def open_snap_install(self):
        snap_install_window = tk.Toplevel(self.root)
        snap_install_window.title("Snap Install")

        # Ustawienie okna jako modalnego
        snap_install_window.transient(self.root)
        snap_install_window.grab_set() 

        search_frame = tk.Frame(snap_install_window)
        search_frame.pack(fill=tk.X, pady=5)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.install_filter_entry = tk.Entry(search_frame)
        self.install_filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.install_filter_entry.bind("<Return>", lambda event: self.search_snap_packages())

        self.install_tree = ttk.Treeview(snap_install_window, columns=("Name", "Version", "Publisher", "Notes", "Summary"), show="headings")
        for col in ("Name", "Version", "Publisher", "Notes", "Summary"):
            self.install_tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.install_tree.column(col, width=150, anchor=tk.W)
        self.install_tree.pack(fill=tk.BOTH, expand=True)

        install_info2_button = tk.Button(snap_install_window, text="Info", command=lambda: self.show_info(self.install_tree))
        install_info2_button.pack(side=tk.LEFT, padx=5, pady=5)

        install_button = tk.Button(snap_install_window, text="Install", command=self.install_package)
        install_button.pack(side=tk.LEFT, padx=5, pady=5)

        snap_install_window.wait_window()
        self.refresh_data()

    def search_snap_packages(self):
        search_query = self.install_filter_entry.get()
        if search_query:
            output = self.execute_command(f"snap search {search_query}")
            lines = output.splitlines()[1:]
            self.install_tree.delete(*self.install_tree.get_children())
            pattern = re.compile(r"^(?P<Name>\S+)\s+(?P<Version>\S+)\s+(?P<Publisher>\S+)\s+(?P<Notes>-|classic)\s+(?P<Summary>.+)$")
            
            for line in lines:
                match = pattern.match(line)
                if match:
                    name = match.group("Name")
                    version = match.group("Version")
                    publisher = match.group("Publisher")
                    notes = match.group("Notes")
                    summary = match.group("Summary")
                    item = (name, version, publisher, notes, summary)
                    self.install_tree.insert("", "end", values=item)

    def install_package_old(self):
        selected_item = self.install_tree.selection()
        if selected_item:
            package_name = self.install_tree.item(selected_item[0])["values"][0]
            if messagebox.askyesno("Confirm", f"Do you want to install {package_name}?"):
                self.execute_command(f"snap install {package_name}")
                messagebox.showinfo("Success", f"Package {package_name} installed.")
                self.refresh_data()

    def remove_package(self, treeview):
        package = self.get_selected_package(treeview)
        if package:
            if messagebox.askyesno("Confirm", f"Are you sure you want to remove {package}?"):
                self.execute_command(f"snap remove {package}")
                self.refresh_data()
    
    def refresh_package(self, treeview):
        package = self.get_selected_package(treeview)
        command = f"snap refresh {package}" if package else "snap refresh"
        self.execute_command(command)
        self.refresh_data()
    
    def disable_package(self, treeview):
        package = self.get_selected_package(treeview)
        if package:
            self.execute_command(f"snap disable {package}")
            self.refresh_data()
    
    def enable_package(self, treeview):
        package = self.get_selected_package(treeview)
        if package:
            self.execute_command(f"snap enable {package}")
            self.refresh_data()
    
    def sort_column(self, col, reverse):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        data.sort(reverse=reverse)
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def get_selected_package_old(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No package selected.")
            return None
        return self.tree.item(selected_item[0])["values"][0]

    def get_selected_package(self, treeview):
        selected_item = treeview.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No package selected.")
            return None
        return treeview.item(selected_item[0])["values"][0]
    
    def show_info_old(self):
        package = self.get_selected_package(treeview)
        if package:
            info = self.execute_command(f"snap info {package}")
            messagebox.showinfo("Package Info", info)

    def execute_command(self, command):
        try:
            result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = result.communicate()
            if stderr:
                messagebox.showerror("Error", stderr)
            return stdout.strip() if not stderr else ""  # Jeśli jest błąd, nie zwracaj stdout
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Command failed: {e}")
            return ""

    def install_package(self):
        selected_item = self.install_tree.selection()
        if selected_item:
            package_name = self.install_tree.item(selected_item[0])["values"][0]
            if messagebox.askyesno("Confirm", f"Do you want to install {package_name}?"):
                # Uruchom proces instalacji w osobnym wątku
                install_thread = threading.Thread(target=self.run_install, args=(package_name,))
                install_thread.start()
                
                # Wyświetl wskaźnik zajętości
                self.show_busy_indicator()

    def run_install(self, package_name):
        """Funkcja uruchamiana w osobnym wątku."""
        try:
            self.execute_command(f"snap install {package_name}")
            self.refresh_data()
            messagebox.showinfo("Success", f"Package {package_name} installed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            # Ukryj wskaźnik zajętości
            self.hide_busy_indicator()

    def show_busy_indicator(self):
        """Pokazuje wskaźnik zajętości."""
        self.busy_window = tk.Toplevel(self.root)
        self.busy_window.title("Working...")
        self.busy_window.transient(self.root)
        self.busy_window.grab_set()
        
        tk.Label(self.busy_window, text="Please wait, installing...").pack(padx=20, pady=20)
        
        # Dodanie przycisku do anulowania
        cancel_button = tk.Button(self.busy_window, text="Cancel", command=self.cancel_install)
        cancel_button.pack(pady=10)
        
        # Ustaw okno jako modalne
        self.busy_window.protocol("WM_DELETE_WINDOW", lambda: None)  # Zablokowanie zamknięcia okna przez użytkownika

    def hide_busy_indicator(self):
        """Ukrywa wskaźnik zajętości."""
        if hasattr(self, 'busy_window') and self.busy_window:
            self.busy_window.destroy()
            self.busy_window = None

    def cancel_install(self):
        """Anuluje proces instalacji."""
        if hasattr(self, 'install_process') and self.install_process:
            try:
                self.install_process.terminate()  # Terminacja procesu
                messagebox.showinfo("Cancelled", "Installation has been cancelled.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not cancel installation: {str(e)}")
            finally:
                self.hide_busy_indicator()


if __name__ == "__main__":
    root = tk.Tk()
    app = SnapManagerApp(root)
    root.mainloop()
