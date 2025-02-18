#!/usr/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Użycie: $0 'polecenie' lista_plików.txt"
    exit 1
fi

polecenie="$1"
lista_plikow="$2"

#if [ ! -f "$lista_plikow" ]; then
#    echo "Plik $lista_plikow nie istnieje!"
#    exit 1
#fi

while IFS= read -r plik; do
    #if [ -f "$plik" ]; then
        echo "Przetwarzanie: $plik"
        eval "$polecenie \"$plik\""
    #else
    #    echo "Plik $plik nie istnieje!"
    #fi
done < "$lista_plikow"
