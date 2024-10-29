#!/usr/bin/bash

# Zmienna tablicowa z nazwami kursorów
kursory=(
"xx"
)

# Przykład użycia: iteracja przez listę kursorów
for kursor in "${kursory[@]}"; do
    if [[ ! -e "$kursor" ]]; then
        # Tworzenie linku symbolicznego do pliku left_ptr
        ln -s left_ptr "$kursor"
        echo "Utworzono link symboliczny: $kursor -> left_ptr"
    else
        echo "Plik $kursor już istnieje, pomijam..."
    fi
done
