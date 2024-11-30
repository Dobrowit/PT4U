#!/usr/bin/python3

import subprocess
import re
from tabulate import tabulate

# Stała kontrolująca skracanie opisu do 80 znaków
SHORTEN_DESCRIPTION = True

# Stała kontrolująca sortowanie wyników po kolumnie Package
SORT_BY_PACKAGE = True

# Stała kontrolująca filtrowanie wyników po nazwie pakietu i opisie
FILTER_BY_QUERY = False

# Stała kontrolująca filtrowanie wyników po wersji
FILTER_BY_VERSION = True

# Stała kontrolująca, czy wyświetlać kolumnę Repo
SHOW_REPO = False

# Stała kontrolująca, czy wyświetlać kolumnę Arch
SHOW_ARCH = False

# Funkcja do wykonania polecenia i zwrócenia wyników
def run_command(command):
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error running command {command}: {e}")
        return ""

# Funkcja do skracania opisu, jeśli ustawiono SHORTEN_DESCRIPTION
def shorten_description(description):
    if SHORTEN_DESCRIPTION:
        return description[:80] + "..." if len(description) > 80 else description
    return description

# Funkcja do usuwania prefiksów wersji (np. 'v')
def normalize_version(version):
    return re.sub(r"[^0-9.]", "", version)

# Parsowanie wyników apt search
def parse_apt_results(output):
    entries = []
    current_entry = {}
    for line in output.splitlines():
        match = re.match(r"^(\S+)/(\S+)\s+(\S+)\s+(\S+)$", line)
        if match:
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                "Package": match.group(1),
                "Repo": match.group(2),
                "Version": match.group(3),
                "Arch": match.group(4),
                "Description": "",
                "Source": "deb"
            }
        elif line.startswith("  ") and current_entry:
            current_entry["Description"] += line.strip() + " "
    if current_entry:
        entries.append(current_entry)
    # Skrócenie opisów, jeśli jest włączone
    for entry in entries:
        entry["Description"] = shorten_description(entry["Description"])
    return entries

# Parsowanie wyników snap search
def parse_snap_results(output):
    entries = []
    for line in output.splitlines()[1:]:  # Pomijamy nagłówek
        parts = line.split(maxsplit=4)  # Podziel dane na kolumny
        if len(parts) == 5:
            entries.append({
                "Package": parts[0],
                "Repo": parts[2],
                "Version": parts[1],
                "Arch": parts[3],
                "Description": shorten_description(parts[4]),
                "Source": "snap"
            })
    return entries

# Parsowanie wyników flatpak search
def parse_flatpak_results(output):
    entries = []
    lines = output.splitlines()[1:]  # Pomijamy nagłówek
    for line in lines:
        parts = line.split("\t")  # Podziel dane na kolumny (flatpak używa tabulatorów)
        if len(parts) >= 6:
            entries.append({
                "Package": parts[2],
                "Repo": parts[5],
                "Version": parts[3],
                "Arch": "-",
                "Description": shorten_description(f"{parts[0]} - {parts[1]}"),
                "Source": "flatpak"
            })
    return entries

# Funkcja do filtrowania wyników po nazwie pakietu i opisie
def filter_entries_by_query(entries, query):
    filtered_entries = []
    for entry in entries:
        if (query.lower() in entry["Package"].lower()) or (query.lower() in entry["Description"].lower()):
            filtered_entries.append(entry)
    return filtered_entries

# Funkcja do filtrowania wyników po wersji
def filter_entries_by_version(entries, version_query):
    filtered_entries = []
    normalized_query = normalize_version(version_query)  # Normalizujemy zapytanie o wersję

    for entry in entries:
        normalized_version = normalize_version(entry["Version"])  # Normalizujemy wersję pakietu
        if normalized_query in normalized_version:
            filtered_entries.append(entry)
    return filtered_entries

# Funkcja wyświetlająca wyniki w formie tabeli
def display_results_table(entries):
    if SORT_BY_PACKAGE:
        entries = sorted(entries, key=lambda x: x["Package"].lower())  # Sortowanie po kolumnie 'Package'
    
    headers = ["Package", "Version", "Description", "Source"]
    
    # Dodaj kolumny Repo i Arch tylko jeśli są ustawione na True
    if SHOW_REPO:
        headers.insert(1, "Repo")
    if SHOW_ARCH:
        headers.insert(3, "Arch")
    
    table = []
    for entry in entries:
        row = [entry["Package"], entry["Version"], entry["Description"], entry["Source"]]
        
        # Dodaj dane Repo i Arch tylko jeśli są ustawione na True
        if SHOW_REPO:
            row.insert(1, entry["Repo"])
        if SHOW_ARCH:
            row.insert(3, entry["Arch"])
        
        table.append(row)
    
    print(tabulate(table, headers=headers, tablefmt="plain"))

if __name__ == "__main__":
    query = input("Enter search query: ").strip()

    # Pobierz wyniki z apt search
    apt_output = run_command(["apt", "search", query])
    apt_entries = parse_apt_results(apt_output)

    # Pobierz wyniki z snap search
    snap_output = run_command(["snap", "search", query])
    snap_entries = parse_snap_results(snap_output)

    # Pobierz wyniki z flatpak search
    flatpak_output = run_command(["flatpak", "search", query])
    flatpak_entries = parse_flatpak_results(flatpak_output)

    # Połącz wszystkie wyniki
    all_entries = apt_entries + snap_entries + flatpak_entries

    # Filtrowanie wyników po nazwie pakietu i opisie, jeśli FILTER_BY_QUERY jest włączone
    if FILTER_BY_QUERY:
        filter_query = input("Enter filter query (search by name or description): ").strip()
        if filter_query:
            all_entries = filter_entries_by_query(all_entries, filter_query)

    # Filtrowanie wyników po wersji, jeśli FILTER_BY_VERSION jest włączone
    if FILTER_BY_VERSION:
        version_query = input("Enter version filter (e.g. 1.1, v1.1): ").strip()
        if version_query:
            all_entries = filter_entries_by_version(all_entries, version_query)

    # Wyświetl wyniki w tabeli
    display_results_table(all_entries)
