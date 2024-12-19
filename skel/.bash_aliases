#!/bin/bash

# To nie alias ale może tu być - dodaje znacznik czasu do historii poleceń
HISTTIMEFORMAT="%F %T "
PATH="$(echo $PATH):$HOME/.skrypty"

alias ..="cd .."
alias ...="cd ../../"
alias ....="cd ../../../"
alias .4="cd ../../../"
alias .5="cd ../../../../"

alias gs="git status -s"
alias gs2="git status"
alias gsall="git log --branches --remotes --tags --graph --oneline --decorate"
alias ipe="curl ipinfo.io/ip; echo"
alias policz="du -m --max-depth 1 | sort -n"
alias apt='sudo apt'
alias cg='cd `git rev-parse --show-toplevel`'
alias cls='clear'
alias count='find . -type f | wc -l'
alias cpuinfo='lscpu'
alias cpv='rsync -ah --info=progress2'
alias dfc="df -h / --output=source,fstype,size,used,avail,pcent"
alias firewall=iptlist
alias getpass='openssl rand -base64 20'
alias getpass2="head -c255 /dev/urandom | base64 | grep -Eoi '[a-z0-9]{12}' | head -n1"
alias gh='history|grep'
alias gksu='pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY'
alias halt='sudo /sbin/halt'
alias headerc='curl -I --compress' # find out if remote server supports gzip / mod_deflate or not #
alias header='curl -I' # get web server headers #
alias ipe='curl ipinfo.io/ip'
alias iptlistfw='sudo /sbin/iptables -L FORWARD -n -v --line-numbers'
alias iptlistin='sudo /sbin/iptables -L INPUT -n -v --line-numbers'
alias iptlistout='sudo /sbin/iptables -L OUTPUT -n -v --line-numbers'
alias iptlist='sudo /sbin/iptables -L -n -v --line-numbers'
alias ipt='sudo /sbin/iptables'
alias left='ls -t -1'
alias lh='ls -lh'
alias lt='ls --human-readable --size -1 -S --classify'
alias meminfo='free --mega -l -t -w -h'
alias mntc='mount | column -t'
alias mnt="mount | awk -F' ' '{ printf \"%s\t%s\n\",\$1,\$3; }' | column -t | egrep ^/dev/ | sort"
alias music='mplayer --shuffle *'
alias now='date +"%T"'
alias nowdate='date +"%d-%m-%Y"'
alias path='echo -e ${PATH//:/\\n}'
alias ping='ping -c 5'
alias playavi='mplayer *.avi'
alias playmp3='for i in *.mp3; do mplayer "$i"; done'
alias playogg='for i in *.ogg; do mplayer "$i"; done'
alias playwave='for i in *.wav; do mplayer "$i"; done'
alias ports='sudo netstat -tulanp'
alias poweroff='sudo /sbin/poweroff'
alias pscpu10='ps aux | sort -nr -k 3 | head -10'
alias pscpu='ps aux | sort -nr -k 3' ## get top process eating cpu ##
alias psmem10='ps aux | sort -nr -k 4 | head -10'
alias psmem='ps aux | sort -nr -k 4' ## get top process eating memory
alias reboot='sudo /sbin/reboot'
alias say='google_speech -e vol 0.40 -l pl 2>/dev/null'
alias say-time='google_speech -e vol 0.40 -l pl "Jest $(date +"%A %d %B") godzina $(date +%R)." 2>/dev/null'
alias sha='shasum -a 256 '
alias shutdown='sudo /sbin/shutdown'
alias snoopdos='clear ; gio monitor -m -d ~/*'
alias snoopg='clear ; dconf watch /'
alias startgit='cd `git rev-parse --show-toplevel` && git checkout master && git pull'
alias synaptic='sudo synaptic'
alias sysinfo='neofetch --cpu_temp C'
alias tcn='mv --force -t ~/.local/share/Trash '
alias untar='tar -zxvf '
alias upgrade='sudo apt -y update && sudo apt -y upgrade ; sudo snap refresh'
alias va='source ./venv/bin/activate'
alias python='python3'
alias ve='python -m venv ./venv'
alias jsonf="python -m json.tool"
alias losuj="python -c '\''from os import urandom; from base64 import b64encode; print(b64encode(urandom(32)).decode(\"utf-8\"))'\''"
alias vlc='vlc *.avi'
alias wget='wget -c '
alias wifi='nmcli dev wifi'
alias x_drv='cat ~/.local/share/xorg/Xorg.0.log | grep drivers'
alias x_gpu='cat ~/.local/share/xorg/Xorg.0.log | grep mem'
alias x_input='cat ~/.local/share/xorg/Xorg.0.log | grep libinput'
alias apt_search='dpkg -S'
alias lsof_reg="lsof | grep REG | awk '{print $NF}' | sort -u"

#alias chprompt_git="export PS1='$([[ -z $(git status -s 2>/dev/null) ]] && echo "\[\e[32m\]" || echo "\[\e[31m\]")$(__git_ps1 "(%s)")\[\e[00m\]\$ '"
#alias nplaywave='for i in /nas/multimedia/wave/*.wav; do mplayer "$i"; done'
#alias nplayogg='for i in /nas/multimedia/ogg/*.ogg; do mplayer "$i"; done'
#alias nplaymp3='for i in /nas/multimedia/mp3/*.mp3; do mplayer "$i"; done'

runnil() {
    echo -en "\033]0;$1\007"
    $1 2>/dev/null
}

ttitle() {
    echo -en "\033]0;$1\007"
}

function show_json() {
    jq -C '.' $1 | less -r
}

function doprzodu() {
    SPECIFIED_BRANCH=$1
    if [[ -z "$SPECIFIED_BRANCH" ]]; then
        echo "Nie podano nazwy gałęzi - podaj ją jako argument"
        return
    fi
    COMMIT_TO_CHECKOUT="$(git rev-list --topo-order HEAD.."$1" | tail -1)"
    if [[ -z "$COMMIT_TO_CHECKOUT" ]]; then
        echo "Brak następnych commitów"
        git checkout "$SPECIFIED_BRANCH"
        return
    else
        git checkout "$COMMIT_TO_CHECKOUT"
    fi
}

function chce_usera() {
    # Tworzenie nowego uzytkownika, z dostepem do sudo i kopia authorized_keys

    # Autor: Radoslaw Karasinski, Grzegorz Ćwikliński, Szymon Hryszko, Artur Stefański

    # if no sudo, then exit
    if [ "$(id -u)" != "0" ]; then
        echo "Musisz uruchomić ten skrypt jako root" 1>&2
        echo "Spróbuj sudo $0"
        exit 1

    fi

    _check_if_user_exits() {
        given_user=$1
        if sudo id "${given_user}" &>/dev/null; then
                echo "Użytkownik ${given_user} już istnieje!"
                exit 1
        fi
    }

    _check_if_user_blank() {
        given_user=$1
        if [ -z "$1" ]; then
            echo "Nie podałeś nazwy użytkownia!"
            exit 1
        fi
    }

    _password_get(){
    username_arg=$1
        while true; do
                    if [ "$username_arg" -eq "0" ]; then
                    # ask for password
                    read -s -p "Podaj hasło (zostaw puste aby wygenerować): " password
                    echo
            fi

            # check if password is blank
            if [ -z "$password" ]; then
                # generate password
                password=$(head -c255 /dev/urandom | base64 | grep -Eoi '[a-z0-9]{12}' | head -n1)
                echo "Twoje hasło to $password"
                break
            fi

            read -sp 'Powtórz hasło: ' password_repeat
            echo

            # if passwords are equal
            if [ "$password" == "$password_repeat" ]; then
                break
            else
                echo "Hasła się nie zgadzają, spróbuj ponownie!"
            fi
        done
    }

    if ! [ -z "$1" ]; then
        username=$1
        username_arg=1
    else
        read -p "Podaj nazwę użytkownika: " username
        username_arg=0
    fi

    _check_if_user_blank $username
    _check_if_user_exits $username
    _password_get $username_arg


    # stworz nowego uzytkownika
    sudo useradd -m -p $(openssl passwd -1 $password) -s /bin/bash "$username" && echo "Uzytkownik $username zostal stworzony"

    # dodaj nowego uzytkownika do sudo
    sudo usermod -aG sudo $username

    ssh_dir="/home/$username/.ssh"

    # stworz folder na ustawienia ssh oraz ustaw odpowiednie prawa
    sudo mkdir -p $ssh_dir
    sudo chmod 700 $ssh_dir

    # stworz authorized_keys oraz ustaw odpowiednie prawa
    sudo touch $ssh_dir/authorized_keys
    sudo chmod 600 $ssh_dir/authorized_keys

    # zmien wlasciciela folderu i plikow
    sudo chown -R $username:$username $ssh_dir

    # skopiuj klucze obecnego uzytkownika do nowo stworzoneg
    cat ~/.ssh/authorized_keys 2>&1 | sudo tee -a $ssh_dir/authorized_keys >/dev/null

    echo "Pomyślnie stworzono użytkownia ${username}."
}

function chce_moje_klucze_ssh() {
    # Author: Koliw (https://github.com/koliwbr/)
    # Platformy: all
    # Kompatybilne z serwerami frog

    # Skrypt pobiera klucze podanego użytkownika z GitHub i dodaje je do zaufanych

    if [[ ! "$1" =~ [a-z]{4,38} ]]; then
        echo -e "\033[5;31m[!]\033[0m\033[1;31m Jako paramert skryptu podaj nazwę użytkownika GitHub\033[0m"
        echo -e "\033[5;31m[!]\033[0m Na przykład \033[0;32m$0 koliwbr\033[0m pobiera klucze użytkownika koliwbr."
        echo -e "\033[5;31m[!]\033[0m Koniecznie zamień na własną nazwę użytkownika!"
        exit 1
    fi

    TMPFILENAME=`mktemp`

    if curl "https://github.com/$1.keys" -sf > $TMPFILENAME; then echo -n; else
        echo -e "\033[5;31m[!]\033[0m Nie znaleziono użytkownika $1 na GitHub"
        rm $TMPFILENAME
        exit 2

    fi

    if [[ ! -s $TMPFILENAME ]]; then
        echo -e "\033[5;31m[!]\033[0m Znaleziono użytkownika $1 na GitHub ale nie masz żadnich kluczy SSH"
        echo -e "\033[5;31m[!]\033[0m Poniżej informacja jak je dodać do konta GitHub"
        echo -e "\033[5;31m[!]\033[0m \033[4mhttps://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#prerequisites\033[0m"
        rm $TMPFILENAME
        exit 3

    fi

    mkdir $HOME/.ssh -p
    cat $TMPFILENAME >> $HOME/.ssh/authorized_keys
    echo Dodano `cat $TMPFILENAME | wc -l` klucz/e/y! Teraz możesz się logować swoimi kluczem/ami z GitHub!
    rm $TMPFILENAME
}
