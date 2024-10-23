#!/bin/bash
## git-mag.sh
##
## Ustawienia
###############################################################################
DEF_COMMIT='Aktualizacja'
GIT_USER='Dobrowit'
GIT_REPO=$(basename $(pwd))

## Sprawdzanie wymaganych zależności
###############################################################################
POLECENIA="git secret-tool"
OK=true

for p in $POLECENIA; do
  if ! command -v "$p" &> /dev/null; then
    echo "Błąd: Polecenie $p nie jest dostępne w systemie." 
    OK=false
  fi
done

if [ "$OK" = false ]; then
  echo "Zakończenie skryptu z powodu brakujących poleceń."
  echo "Zainstaluj brakujące polecenia."
  sudo apt install git libsecret-tools
  if [ "$?" = "0" ]; then
	  echo "Zainstalowano pomyślnie."
  else
    exit 1
	fi
fi

## Obsługa opcji -i - Informacje o konfiguracji
###############################################################################
if [ "$1" = "-i" ]; then
  echo "Ustawienia:"
  echo "  GIT_REPO=$GIT_REPO"
  echo "  GIT_USER=$GIT_USER"
  echo "  DEF_COMMIT=$DEF_COMMIT"
  echo "Nazwa skryptu - $0"
  exit 0
fi

## Obsługa opcji -h - Pomoc
###############################################################################
if [ "$1" = "-h" ]; then
  echo "GitMag to pomocnik dla konsolowego polecenia git."
  echo "Pozwala zapisać do bezpiecznego magazynu token potrzebny do pracy z GitHub."
  echo "Token możesz wygenerować na stronie https://github.com/settings/tokens"
  echo "Zaleca się ustawianie niezbędnych uprawnień i w miarę krótkiego czasu ważności."
  echo "Dostępne opcje:"
  echo "  -i - informacja o konfiguracji"
  echo "  -t - zapisanie tokena"
  echo "  -l - zalogowanie się do repo (nazwa repo brana jest z nazwy bieżącego katalogu)"
  echo "  -c - commit z add i push"
  echo ""
  echo "  -du <user>   - ustalenie nowego użytkownika"
  echo "  -dc <commit> - ustalenie domyślnego opisu commita"
  exit 0
fi

## Obsługa opcji -t - Zapamiętanie tokena
###############################################################################
if [ "$1" = "-t" ]; then
  secret-tool store --label="GitHub token" "application" "GitHub"
  if [ $? -eq 0 ]; then
    echo "Token zapisano w bazie kluczy."
    exit 0
  else
    echo "Niepowodzenie!"
    exit 1
  fi
fi

## Obsługa opcji -l - zalogowanie się do repo
###############################################################################
if [ "$1" = "-l" ]; then
  TOKEN=$(secret-tool lookup "application" "GitHub")
  git remote set-url origin https://$TOKEN@github.com/$GIT_USER/$GIT_REPO
  exit 0
fi

## Obsługa opcji -c - commit z add i push 
###############################################################################
if [ "$1" = "-c" ]; then
  git add ./ ; git commit -m $DEF_COMMIT ; git push origin main
  exit 0
fi

## Obsługa opcji -dc <commit>
###############################################################################
if [ "$1" = "-dc" ]; then
  sed -i 's/DEF_COMMIT='.*'/DEF_COMMIT='$2'/' $0
  exit 0
fi

## Obsługa opcji -du <user>
###############################################################################
if [ "$1" = "-du" ]; then
  sed -i 's/GIT_USER='.*'/GIT_USER='$2'/' $0
  exit 0
fi
