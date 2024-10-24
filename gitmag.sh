#!/bin/bash
## GitMag.sh
##
## Ustawienia i kolorki
###############################################################################
DEF_COMMIT="Aktualizacja"
GIT_USER="Dobrowit"
GIT_REPO=$(basename $(pwd))

RED="\033[31m"
YELLOW="\033[33m"
WHITE="\033[37m"
GREEN="\033[32m"
BLUE="\033[34m"
RESET="\033[0m"

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
  echo -e "\nUstawienia:"
  echo -e "        Nazwa repozytorium: ${RED}${GIT_REPO}${RESET}"
  echo -e "  Nazwa użytkownika GitHub: ${RED}${GIT_USER}${RESET}"
  echo -e "     Domyślny opis commita: ${RED}${DEF_COMMIT}${RESET}\n"
  exit 0
fi

## Obsługa opcji -h - Pomoc
###############################################################################
if [ "$1" = "-h" ]; then
  echo -e "\n${YELLOW}GitMag to pomocnik dla konsolowego polecenia git.${RESET}"
  echo "Pozwala zapisać do bezpiecznego magazynu token potrzebny do pracy z GitHub."
  echo -e "Token możesz wygenerować na stronie ${BLUE}https://github.com/settings/tokens${RESET}"
  echo "Zaleca się ustawianie niezbędnych uprawnień i w miarę krótkiego czasu ważności."
  echo -e "\n${YELLOW}Dostępne opcje:${RESET}"
  echo -e "  ${RED}-i${RESET}  - informacja o konfiguracji"
  echo -e "  ${RED}-t${RESET}  - zapisanie tokena"
  echo -e "  ${RED}-l${RESET}  - zalogowanie się do repo (nazwa repo brana jest z nazwy bieżącego katalogu)"
  echo -e "  ${RED}-c${RESET}  - commit z add"
  echo -e "  ${RED}-cp${RESET} - commit z add i push"
  echo -e "  ${RED}-du <user>${RESET}   - ustalenie domyślnego użytkownika"
  echo -e "  ${RED}-dc <commit>${RESET} - ustalenie domyślnego opisu commita\n"
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
  echo -e "${YELLOW}git remote set-url origin https://<token>@github.com/${GIT_USER}/${GIT_REPO}${RESET}"
  git remote set-url origin https://$TOKEN@github.com/$GIT_USER/$GIT_REPO
  exit 0
fi

## Obsługa opcji -c - commit z add
###############################################################################
if [ "$1" = "-c" ]; then
  echo -e "${YELLOW}git add ./${RESET}"
  git add ./
  echo -e "${YELLOW}git commit -m ${DEF_COMMIT}${RESET}"
  git commit -m $DEF_COMMIT
  exit 0
fi

## Obsługa opcji -cp - commit z add i push 
###############################################################################
if [ "$1" = "-cp" ]; then
  echo -e "${YELLOW}git add ./${RESET}"
  git add ./
  echo -e "${YELLOW}git commit -m ${DEF_COMMIT}${RESET}"
  git commit -m $DEF_COMMIT
  echo -e "${YELLOW}git push orign main${RESET}"
  git push origin main
  exit 0
fi

## Obsługa opcji -dc <commit>
###############################################################################
if [ "$1" = "-dc" ]; then
  sed -i -e '6s/^DEF_COMMIT='.*'/DEF_COMMIT='$2'/' $0
  exit 0
fi

## Obsługa opcji -du <user>
###############################################################################
if [ "$1" = "-du" ]; then
  sed -i -e '7s/^GIT_USER="[^"]*"$/GIT_USER="'"$2"'"/' $0
  exit 0
fi
