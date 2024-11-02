#!/bin/bash
## GitMag.sh
##
## Ustawienia i kolorki
###############################################################################
DEF_COMMIT="Aktualizacja"
GIT_USER="Dobrowit"
GIT_REPO=$(basename $(pwd))
WORK_DIR="/home/radek/WORK/GitHub/"

RED="\033[31m"
YELLOW="\033[33m"
WHITE="\033[37m"
GREEN="\033[32m"
BLUE="\033[34m"
RESET="\033[0m"

## Sprawdzanie wymaganych zależności
###############################################################################
POLECENIA="git secret-tool dialog"
OK=true

sprawdz_system() {
    if grep -q "Debian" /etc/os-release; then
        return 0
    elif grep -q "Ubuntu" /etc/os-release; then
        return 0
    else
        return 1
    fi
}

wait_for_actions() {
    if gh auth status > /dev/null 2>&1; then
        echo -e "${RED}Czekam na wykonanie wyzwolonych akcji:${RESET}"

        # Flaga do śledzenia stanu
        has_jobs=false
        first_line=true
        
        while true; do
            # Sprawdzamy listę bieżących zadań
            running_jobs=$(gh run list -R Dobrowit/$GIT_REPO --status in_progress)

            # Jeśli lista zadań nie jest pusta
            if [ -n "$running_jobs" ]; then
                if ! $has_jobs && $first_line; then
                    # echo -n "#"
                    first_line=false
                fi
                #echo "$running_jobs"
                echo -e -n "${BLUE}#${RESET}"
                has_jobs=true
            else
                # Jeśli wcześniej były zadania i teraz lista jest pusta
                if $has_jobs; then
                    echo -e "\n${GREEN}Wszystkie zadania zostały zakończone.${RESET}\n"
                    break
                else
                    echo -n "#"
                fi
            fi
            sleep 2
        done
    else
        echo "Nie jesteś zalogowany do GitHub CLI. Zaloguj się, używając 'gh auth login'."
    fi
}

for p in $POLECENIA; do
  if ! command -v "$p" &> /dev/null; then
    echo "Błąd: Polecenie $p nie jest dostępne w systemie." 
    OK=false
  fi
done

if sprawdz_system; then
  if [ "$OK" = false ]; then
    sudo apt install git libsecret-tools dialog
    if [ "$?" = "0" ]; then
	    echo "Zainstalowano pomyślnie."
    else
      exit 1
	  fi
  fi
else
    echo -e "${RED}Zainstaluj brakujące polecenia!${RESET}"
    exit 1
fi

## Domyślny komunikat bez opcji
###############################################################################
if [ "$1" = "" ]; then
  echo -e "\n${YELLOW}GitMag - pomocnik dla git'a.${RESET}"
  echo -e "\n$(basename $0) ${RED}-h${RESET}    - krótka pomoc\n"
  exit 0
fi

## Pomoc
###############################################################################
if [ "$1" = "-h" ]; then
  echo -e "\n${YELLOW}GitMag to pomocnik dla konsolowego polecenia git.${RESET}"
  echo "Pozwala zapisać do bezpiecznego magazynu token potrzebny do pracy z GitHub."
  echo -e "Token możesz wygenerować na stronie ${BLUE}https://github.com/settings/tokens${RESET}"
  echo "Zaleca się ustawianie tylko niezbędnych uprawnień i max 7 dni czasu ważności."
  echo -e "Token może być bezpiecznie przekazany przez linię poleceń (${RED}-l${RESET})."
  echo -e "Po zakończonej pracy można w sprytny sposób usunąć token z pliku config (${RED}-r${RESET})."
  echo -e "\n${YELLOW}Dostępne opcje:${RESET}"
  echo -e "  ${RED}-i${RESET}  - informacja o konfiguracji"
  echo -e "  ${RED}-t${RESET}  - zapisanie tokena w systemowym magazynie kluczy"
  echo -e "  ${RED}-l${RESET}  - zalogowanie się do repo (nazwa repo brana jest z nazwy bieżącego katalogu)"
  echo -e "  ${RED}-r${RESET}  - wylogowanie się z repo (usunięcie tokena z pliku config)"
  echo -e "  ${RED}-c${RESET}  - commit z add"
  echo -e "  ${RED}-p${RESET}  - commit z add i push"
  echo -e "  ${RED}-w${RESET}  - przejście do katalogu roboczego"
  echo -e "  ${RED}-a${RESET}  - pobiera wszystkie repozytoria"
  echo -e "  ${RED}-dw${RESET} - ustalenie domyślnego..."
  echo -e "  ${RED}-du <user>${RESET}   - ustalenie domyślnego użytkownika"
  echo -e "  ${RED}-dc <commit>${RESET} - ustalenie domyślnego opisu commita"
  echo -e "  ${RED}-p -w${RESET}        - tak jak ${RED}-p${RESET} plus oczekiwanie na zakończenie wyzwolonych akcji (np. GitHub Pages)\n"

  exit 0
fi

## Sprawdzanie czy jesteś we właściwym miejscu
###############################################################################
sprawdz_git() {
    if [ -e ".git/" ]; then
      echo -e "\n${GREEN}OK - jesteś w repozytorium GIT.${RESET}\n"
      return 0
    else
      echo -e "\n${RED}Nie jesteś w repozytorium GIT!${RESET}\n"
      echo "Pobierz odpowiednie repo. wydając polecenia - np.:"
      echo -e "${YELLOW}git clone https://github.com/Dobrowit/PT4U${RESET}"
      echo -e "${YELLOW}cd ./PT4U${RESET}\n"
      return 1
    fi
}

## Informacje o konfiguracji
###############################################################################
if [ "$1" = "-i" ]; then
  if sprawdz_git; then
    TOKEN=$(secret-tool lookup "application" "GitHub")
    echo -e "        Nazwa repozytorium: ${RED}${GIT_REPO}${RESET}"
    echo -e "  Nazwa użytkownika GitHub: ${RED}${GIT_USER}${RESET}"
    echo -e "                     Token: ${RED}${TOKEN}${RESET}"
    echo -e "        Adres repozytorium: ${RED}https://github.com/$GIT_USER/$GIT_REPO${RESET}"
    echo -e "     Domyślny opis commita: ${RED}${DEF_COMMIT}${RESET}\n"

    # curl -s "https://api.github.com/users/$GIT_USER/repos?per_page=100" |
    # jq -r '.[] | select(.fork == false) | "\(.name) - \(.description // "Brak opisu")"'


    # Pobranie listy repozytoriów z GitHub
    REPOS=$(curl -s "https://api.github.com/users/$GIT_USER/repos?per_page=100" |
    jq -r '.[] | select(.fork == false) | "\(.name)\t\(.description // "Brak opisu")"')
    
    # Tworzenie tablicy dla Dialog
    OPTIONS=()
    while IFS= read -r line; do
        # Dodanie każdej pozycji do tablicy z checkboxem
        nazwa=$(echo "$line" | awk -F'\t' '{print $1}')
        opis=$(echo "$line" | awk -F'\t' '{print $2}')
        OPTIONS+=("$nazwa" "$opis" off "$opis")
    done <<< "$REPOS"
    
    # Wywołanie Dialog
    dialog \
      --title "Wybór Repozytoriów" \
      --item-help \
      --colors \
      --backtitle "gitmag" \
      --separate-output \
      --checklist "Wybierz repozytoria:" 20 70 15 "${OPTIONS[@]}" 3>&1 1>&2 2>&3

    # Sprawdzenie, czy użytkownik potwierdził wybór
    if [ $? -eq 0 ]; then
        echo "Wybrane repozytoria:"
        echo "$REPLY"
    else
        echo "Anulowano."
    fi
    
    exit 0
  fi
fi

## Zapamiętanie tokena w systemowej bazie kluczy
###############################################################################
if [ "$1" = "-t" ]; then
  secret-tool clear "application" "GitHub"
  if [ "$2" = "" ]; then
    read -p "GIT_TOKEN > " T
    echo -n "$T" | secret-tool store --label="GitHub token" "application" "GitHub"
  else
    echo -n "$2" | secret-tool store --label="GitHub token" "application" "GitHub"
  fi
  if [ $? -eq 0 ]; then
    echo "Token zapisano w bazie kluczy."
    exit 0
  else
    echo "Niepowodzenie!"
    exit 1
  fi
fi

## Zalogowanie się do repo
###############################################################################
if [ "$1" = "-l" ]; then
  if sprawdz_git; then
    TOKEN=$(secret-tool lookup "application" "GitHub")
    echo -e "${YELLOW}git remote set-url origin https://<token>@github.com/${GIT_USER}/${GIT_REPO}${RESET}"
    git remote set-url origin https://$TOKEN@github.com/$GIT_USER/$GIT_REPO
    exit 0
  fi
fi

## Wylogowanie się z repo (usunięcie tokena z pliku config)
###############################################################################
if [ "$1" = "-r" ]; then
  if sprawdz_git; then
    echo -e "${YELLOW}git remote set-url origin https://github.com/${GIT_USER}/${GIT_REPO}${RESET}"
    git remote set-url origin https://github.com/$GIT_USER/$GIT_REPO
    exit 0
  fi
fi

## Commit z add
###############################################################################
if [ "$1" = "-c" ]; then
  if sprawdz_git; then
    echo -e "${YELLOW}git add ./${RESET}"
    git add ./
    echo -e "${YELLOW}git commit -m ${DEF_COMMIT}${RESET}"
    git commit -m $DEF_COMMIT
    exit 0
  fi
fi

## Commit z add i push 
###############################################################################
if [ "$1" = "-p" ]; then
  if sprawdz_git; then
    echo -e "${YELLOW}git add ./${RESET}"
    git add ./
    echo -e "${YELLOW}git commit -m ${DEF_COMMIT}${RESET}"
    git commit -m $DEF_COMMIT
    echo -e "${YELLOW}git push orign main${RESET}"
    git push origin main
    if [ "$2" = "-w" ]; then
      wait_for_actions
    fi
    exit 0
  fi
fi

## Uwaga - problem z dziedziczeniem. To nie zadziała.
###############################################################################
if [ "$1" = "-w" ]; then
  cd $WORK_DIR
  directories=($(find . -maxdepth 1 -type d ! -path .))
  echo "Wybierz repozytorium:"
  pwd
  select dir in "${directories[@]}"; do
      if [[ -n "$dir" ]]; then
          echo -n "Wybrano katalog: "
          cd $dir
          pwd
          break
      else
          echo "Nieprawidłowy wybór, spróbuj ponownie."
      fi
  done
  exit 0
fi

## Ustalenie domyślnego... SPRAWDZIĆ BETA
###############################################################################
if [ "$1" = "-dw" ]; then
  pwd
  sed -i -e '9s/^WORK_DIR='.*'/DEF_COMMIT='$(pwd)'/' $0
  exit 0
fi

## Ustalenie domyślnego opisu commita
###############################################################################
if [ "$1" = "-dc" ]; then
  sed -i -e '6s/^DEF_COMMIT='.*'/DEF_COMMIT='$2'/' $0
  exit 0
fi

## Ustalenie domyślnego użytkownika
###############################################################################
if [ "$1" = "-du" ]; then
  sed -i -e '7s/^GIT_USER="[^"]*"$/GIT_USER="'"$2"'"/' $0
  exit 0
fi

## Pobiera wszystkie repozytoria - BETA
###############################################################################
if [ "$1" = "-a" ]; then
  TARGET_DIR="/home/radek/WORK/github_work"
  TOKEN=$(secret-tool lookup "application" "GitHub")
  REPOS=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/user/repos?per_page=100" | grep -o 'git@[^"]*')
  cd "$TARGET_DIR"
  for repo in $REPOS; do
      git clone "$repo"
  done
  exit 0
fi
