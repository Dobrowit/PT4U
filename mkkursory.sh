#!/usr/bin/bash

# Sprawdzenie czy plik kursor.txt istnieje w bieżącym katalogu
if [[ ! -f "kursory.txt" ]]; then
    echo "Brak pliku kursor.txt w bieżącym katalogu."
    exit 1
fi

# Pętla po liniach pliku kursor.txt
while read -r line; do
    # Sprawdzenie, czy plik o tej nazwie już istnieje
    if [[ ! -e "$line" ]]; then
        # Tworzenie linku symbolicznego do pliku left_ptr
        ln -s left_ptr "$line"
        echo "Utworzono link symboliczny: $line -> left_ptr"
    else
        echo "Plik $line już istnieje, pomijam..."
    fi
done < "kursory.txt"
