#!/bin/bash
## Ustawienia
###############################################################################
SRV='192.168.0.100'
OPT="uid=$UID,iocharset=utf8,rw,noperm,file_mode=0777,dir_mode=0777"
BASEDIR="$HOME/mnt"
BASEDIR_GVFS="$HOME/mnt-gvfs"
###############################################################################

NAZWA=$(basename $0)
CFG="$HOME/.${NAZWA%.sh}"
USR=$USER

## Sprawdzanie lokalizacji systemowej i ustawienie języka
###############################################################################
LOCALE=$(locale | grep LANG | cut -d '=' -f 2)

if [[ $LOCALE == pl_PL* ]]; then
  # Polish translations
  K01="Błąd: Polecenie %s nie jest dostępne w systemie."
  K02="Zakończenie skryptu z powodu brakujących poleceń."
  K03="Zainstaluj brakujące polecenia."
  K04="Zapisano adres serwera:"
  K05="Ustawienia:"
  K06="\nAdres serwera wczytano z pliku"
  K07="Nic nie jest zamontowane."
  K08="Adres serwera:"
  K09="Użytkownik serwera:"
  K10="Hasło zapisano w bazie kluczy."
  K11="Niepowodzenie!"
  K12="Nie podano nazwy użytkownika!"
  K13="Użytkownik serwera:"
  K14="Nie podano nazwy użytkownika!"
  K15="Lista udziałów CIFS na serwerze"
  K16="Odmontowywanie udziału CIFS..."
  K17="Błąd: Nie udało się odmontować udziału."
  K18="Udział CIFS został odmontowany pomyślnie."
  K19="Odmontowano"
  K20="Zamontowano"
  K21="Nie znam opcji"
  K22="Błąd: Nie udało się stworzyć katalogu"
  K23="Udział %s nie znajduje się w zasobach serwera!"

  H1="$NAZWA [opcja]
 <share>            Montowanie zasobu sieciowego <share> dla bieżącego użytkownika
 <share> -u <user>  Montowanie zasobu sieciowego <share> dla użytkownika <user>
 -a                 Montowanie wszystkich zasobów (z listy -ls)
 -g                 Montowanie wszystkich zasobów (z listy -ls) przez gvfs
 <share> -d         Odmontowanie zasobu <share>
 -da                Odmontowanie wszystkich zasobów (z listy -ls)
 -gd                Odmontowanie wszystkich zasobów (z listy -ls) przez gvfs
 -ls                Lista udziałów na serwerze dla bieżącego użytkownika
 -ls -u <user>      Lista udziałów na serwerze dla użytkownika <user>
 -l                 Lista zamontowanych udziałów
 -s <ip>            Zapamiętanie adresu serwera SMB
 -p <user>          Zapamiętanie hasła dla danego użytkownika <user>
 -i                 Informacje o konfiguracji
 -h                 Pomoc"
  H2="\e[1m\e[4mSKŁADNIA\e[0m
Montowanie zasobu sieciowego SMB o nazwie \e[1m<share>\e[0m dla bieżącego użytkownika:
  \e[1m$NAZWA <share>\e[0m

Montowanie wszystkich zasobów (z listy -ls):
  \e[1m$NAZWA -a\e[0m

Montowanie zasobu sieciowego SMB o nazwie \e[1m<share>\e[0m dla użytkownika \e[1m<user>\e[0m:
  \e[1m$NAZWA <share> -u <user>\e[0m
  
Odmontowanie zasobu \e[1m<share>\e[0m:
  \e[1m$NAZWA <share> -d\e[0m

Odmontowanie wszystkich zasobów (z listy -ls):
  \e[1m$NAZWA -da\e[0m

Lista udziałów na serwerze dla bieżącego użytkownika:
  \e[1m$NAZWA -ls\e[0m

Lista udziałów na serwerze dla użytkownika \e[1m<user>\e[0m:
  \e[1m$NAZWA -ls -u <user>\e[0m

Lista zamontowanych udziałów:
  \e[1m$NAZWA -l\e[0m
  
Zapamiętanie adresu serwera SMB:
  \e[1m$NAZWA -s <ip>\e[0m

Zapamiętanie hasła dla danego użytkownika \e[1m<user>\e[0m:
  \e[1m$NAZWA -p <user>\e[0m
 
Informacje o konfiguracji:
  \e[1m$NAZWA -i\e[0m
  
Pomoc:
  \e[1m$NAZWA -h\e[0m

Nazwa zasobu \e[1m<share>\e[0m nie jest pełnym adresem. Jeśli zasób ma adres:
  \e[1msmb://$SRV/mojepliki\e[0m
to pod \e[1m<share>\e[0m podstawiasz:
  \e[1mmojepliki\e[0m


\e[1m\e[4mKATALOG DO MONTOWANIA ZASOBÓW\e[0m
  \e[1m$BASEDIR\e[0m
Jeśli ten katalog nie istnieje to będzie utworzony. Poszczególne zasoby będą
montowane w podkatalogach o nazwach takich jak dany zasób. Dla zasobu o nazwie
\e[1mmojepliki\e[0m będzie to katalog \e[1m$BASEDIR/mojepliki\e[0m.


\e[1m\e[4mHASŁO\e[0m
Hasło dla podanego użytkownika pobierane jest z bazy kluczy. Jeśłi nie podasz
nazwy użytkownika to użyty zostanie bieżący użytkownik. Do edycji bazy użyj
narzędzi \e[1mseahorse\e[0m (GUI) lub \e[1msecret-tool\e[0m (CLI). Hasło jest wyszukiwane przez trzy
klucze:
  \e[1mprotocol = 'smb'
  user = $USER
  server = $SRV\e[0m

Hasło można dodać do bazy za pomocą menadżera plików \e[1mNautilus\e[0m. Zamontuj zasób.
Jeśli pojawi się pytanie jak zapamiętć hasło - zapamiętaj na stałe.
Aby edytować i przeglądać tak zapamiętane hasła - użyj aplikacji \e[1mseahorse\e[0m.

Możesz także użyć polecenia:
  \e[1msecret-tool store protocol smb user $USER server $SRV\e[0m


\e[1m\e[4mADRES SERWERA\e[0m
Adres serwera musi być podany w postaci adresu IP lub domeny - np.
  \e[1m$SRV\e[0m
Adres można zmienić bezpośrednio w tym skrypcie, na początku w zmiennej \e[1mSRV\e[0m lub
zapisując go w pliku \e[1m$CFG\e[0m.


\e[1m\e[4mNAZWA UŻYTKOWNIKA\e[0m
Nazwę użytkownika należy podać jeśli bieżący użytkownik jest inny niż ten na
serwerze SMB."
else
  # English translations
  K01="Error: Command %s is not available on the system."
  K02="Terminating the script due to missing commands."
  K03="Install the missing commands."
  K04="Server address saved: "
  K05="Settings:"
  K06="\nServer address loaded from file "
  K07="Nothing is mounted."
  K08="Server address: "
  K09="Server user:"
  K10="Password saved in the keyring."
  K11="Failure!"
  K12="No username provided!"
  K13="Server user:"
  K14="No username provided!"
  K15="List of CIFS shares on server"
  K16="Unmounting CIFS share..."
  K17="Error: Failed to unmount the share."
  K18="CIFS share was successfully unmounted."
  K19="Unmounted "
  K20="Mounted "
  K21="I don't recognize the option"
  K22="Error: Failed to create directory"
  K23="Share %s is not available on the server!"

  H1="$NAZWA [option]
 <share>            Mount network share <share> for the current user
 <share> -u <user>  Mount network share <share> for the user <user>
 -a                 Mount all shares (from the list -ls)
 <share> -d         Unmount share <share>
 -da                Unmount all shares (from the list -ls)
 -ls                List shares on the server for the current user
 -ls -u <user>      List shares on the server for the user <user>
 -l                 List mounted shares
 -s <ip>            Save the SMB server address
 -p <user>          Save the password for the user <user>
 -i                 Configuration information
 -h                 Help"
  H2="\e[1m\e[4mSYNTAX\e[0m
Mounting the SMB network share named \e[1m<share>\e[0m for the current user:
  \e[1m$NAZWA <share>\e[0m

Mounting all shares (from the list -ls):
  \e[1m$NAZWA -a\e[0m

Mounting the SMB network share named \e[1m<share>\e[0m for the user \e[1m<user>\e[0m:
  \e[1m$NAZWA <share> -u <user>\e[0m
  
Unmounting the share \e[1m<share>\e[0m:
  \e[1m$NAZWA <share> -d\e[0m

Unmounting all shares (from the list -ls):
  \e[1m$NAZWA -da\e[0m

List of shares on the server for the current user:
  \e[1m$NAZWA -ls\e[0m

List of shares on the server for the user \e[1m<user>\e[0m:
  \e[1m$NAZWA -ls -u <user>\e[0m

List of mounted shares:
  \e[1m$NAZWA -l\e[0m
  
Saving the SMB server address:
  \e[1m$NAZWA -s <ip>\e[0m

Saving the password for the user \e[1m<user>\e[0m:
  \e[1m$NAZWA -p <user>\e[0m
 
Configuration information:
  \e[1m$NAZWA -i\e[0m
  
Help:
  \e[1m$NAZWA -h\e[0m

The share name \e[1m<share>\e[0m is not a full address. If the share has the address:
  \e[1msmb://$SRV/myfiles\e[0m
then for \e[1m<share>\e[0m, you enter:
  \e[1mmyfiles\e[0m


\e[1m\e[4mDIRECTORY FOR MOUNTING SHARES\e[0m
  \e[1m$BASEDIR\e[0m
If this directory does not exist, it will be created. Individual shares will
be mounted in subdirectories named after the share. For a share named
\e[1mmyfiles\e[0m, the directory will be \e[1m$BASEDIR/myfiles\e[0m.


\e[1m\e[4mPASSWORD\e[0m
The password for the specified user is retrieved from the keyring. If you do
not provide a username, the current user will be used. To edit the keyring, use
\e[1mseahorse\e[0m (GUI) or \e[1msecret-tool\e[0m (CLI). The password is searched by three
keys:
  \e[1mprotocol = 'smb'
  user = $USER
  server = $SRV\e[0m

You can add the password to the keyring using the \e[1mNautilus\e[0m file manager. Mount the share.
If prompted to remember the password, save it permanently.
To edit and view stored passwords, use the \e[1mseahorse\e[0m application.

You can also use the command:
  \e[1msecret-tool store protocol smb user $USER server $SRV\e[0m


\e[1m\e[4mSERVER ADDRESS\e[0m
The server address must be provided as an IP address or domain, e.g.:
  \e[1m$SRV\e[0m
You can change the address directly in this script, at the beginning in the variable \e[1mSRV\e[0m or
by saving it in the file \e[1m$CFG\e[0m.


\e[1m\e[4mUSERNAME\e[0m
You must provide a username if the current user is different from the one on
the SMB server."
fi

## Definica funkcji - pomoc
###############################################################################
function help1() {
  echo -e "$H1"
}

function help2() {
  echo -e "$H2" | less -R
}

function czysciciel() {
  if [ -z "$(ls -A "$BASEDIR" 2>/dev/null)" ]; then
      rmdir "$BASEDIR"
  fi
  if [ -z "$(ls -A "$BASEDIR_GVFS" 2>/dev/null)" ]; then
      rmdir "$BASEDIR_GVFS"
  fi
}

## Sprawdzanie wymaganych zależności
###############################################################################
POLECENIA="smbclient secret-tool printf gio"
OK=true

for p in $POLECENIA; do
    if ! command -v "$p" &> /dev/null; then
        echo "$(printf "$K01" "$p")" # "Błąd: Polecenie $p nie jest dostępne w systemie."
        OK=false
    fi
done

if [ "$OK" = false ]; then
    echo $K02 # Zakończenie skryptu z powodu brakujących poleceń.
    echo $K03 # Zainstaluj brakujące polecenia.
    exit 1
fi

## Wczytanie adresu serwera z pliku konfiguracyjnego
###############################################################################
if [ -e $CFG ] && [ -f $CFG ]; then
  SRV=$(cat "$CFG")
fi

## Wyświetlenie szybkiej pomocy jeśli nie podano żadnych opcji
###############################################################################
if [ -z "$1" ]; then
  help1
  exit 0
fi

## Obsługa opcji -s <ip> - Zapamiętanie adresu serwera SMB
###############################################################################
if [ "$1" = "-s" ]; then
  echo "$2" >"$CFG"
  echo "$K04 $2" # Zapisano adres serwera: $2
  exit 0
fi

## Obsługa opcji -i - Informacje o konfiguracji
###############################################################################
if [ "$1" = "-i" ]; then
  echo $K05 # Ustawienia:
  echo "  USR=$USR"
  echo "  NAZWA=$NAZWA"
  echo "  BASEDIR=$BASEDIR"
  echo "  SRV=$SRV"
  echo "  OPT=$OPT"
  echo "  CFG=$CFG"
  if [ -e $CFG ] && [ -f $CFG ]; then
    echo -e "$K06 $CFG" # \nAdres serwera wczytano z pliku $CFG
  fi
  exit 0
fi

## Obsługa opcji -h - Pomoc
###############################################################################
if [ "$1" = "-h" ]; then
  help2
  exit 0
fi

## Obsługa opcji -l - Lista zamontowanych udziałów
###############################################################################
if [ "$1" = "-l" ]; then
  df -h -t cifs 2>/dev/null
  ls /run/user/$UID/gvfs
  # POPRAWIĆ!!!!
  if [ $? -eq 0 ]; then
      exit 0
    else
      echo $K07 # Nic nie jest zamontowane.
      exit 1
  fi
  exit 1
fi

## Obsługa opcji -p <user> - Zapamiętanie hasła dla danego użytkownika <user>
###############################################################################
if [ "$1" = "-p" ]; then
  if [[ -n "$2" ]]; then
    USR=$2
    echo "$K08 $SRV" # Adres serwera: $SRV
    echo "$K09 $USR" # Użytkownik serwera: $USR
    secret-tool store protocol smb user $USR server $SRV
    if [ $? -eq 0 ]; then
      echo $K10 # Hasło zapisano w bazie kluczy.
      exit 0
    else
      echo $K11 # Niepowodzenie!
      exit 1
    fi
  else
    echo $K12 # Nie podano nazwy użytkownika!
    exit 1
  fi
fi

## Obsługa opcji -u - użytkownik serwera
## Zmienna PAS jest używana w dalszych częściach skryptu
###############################################################################
PAS=$(secret-tool lookup protocol smb user $USER)
if [ "$2" = "-u" ]; then
  if [[ -n "$3" ]]; then
    USR=$3
    echo "$K13 $3" # Użytkownik serwera: $3
    PAS=$(secret-tool lookup protocol smb user $USR)
  else
    echo $K14 # Nie podano nazwy użytkownika!
    exit 1
  fi
fi

## Obsługa opcji -ls - Lista udziałów na serwerze
###############################################################################
if [ "$1" = "-ls" ]; then
  echo "$K15 $SRV:" # Lista udziałów CIFS na serwerze $SRV:
  smbclient -L //$SRV --user=$USR --password=$PAS | awk '$2 == "Disk" {print "  "$1}'
  exit 0
fi

## Obsługa opcji -d - Odmontowanie zasobu
## Zmienne MNTDIR i SHARE są używane w dalszych częściach skryptu
###############################################################################
SHARE="$1"
MNTDIR="$BASEDIR/$SHARE/"
if [ "$2" = "-d" ]; then
  echo $K16 # Odmontowywanie udziału CIFS...
  sudo umount "$MNTDIR"
  if [ $? -ne 0 ]; then
    echo $K17 # Błąd: Nie udało się odmontować udziału.
    exit 1
  fi
  echo $K18 # Udział CIFS został odmontowany pomyślnie.
  rmdir $MNTDIR
  czysciciel
  exit 0
fi

## Obsługa opcji -da
###############################################################################
LISTA=$(smbclient -L //$SRV --user=$USR --password=$PAS | awk '$2 == "Disk" {print $1}')
if [ "$1" == "-da" ]; then
  for ITEM in $LISTA; do
    MNTDIR="$BASEDIR/$ITEM/"
    sudo umount "$MNTDIR" 2>/dev/null
    if [ $? -eq 0 ]; then
      echo "$K19 $MNTDIR" # Odmontowano $MNTDIR
      rmdir $MNTDIR
    fi
  done
  czysciciel
  exit 0
fi

## Obsługa opcji -a
###############################################################################
if [ "$1" == "-a" ]; then
  for ITEM in $LISTA; do
    MNTDIR="$BASEDIR/$ITEM/"
    mkdir -p "$MNTDIR"
    sudo mount -t cifs -o username=$USR,password=$PAS,$OPT //$SRV/$ITEM $MNTDIR
    if [ $? -eq 0 ]; then
      echo "$K20 $MNTDIR" # Zamontowano $MNTDIR
    fi
  done
  exit 0
fi

## Obsługa opcji -gd
###############################################################################
if [ "$1" == "-gd" ]; then
  for ITEM in $LISTA; do
    MNTDIR="$BASEDIR_GVFS/smb-share:server=$SRV,share=$ITEM"
    gio mount -u smb://$SRV/$ITEM
    if [ $? -eq 0 ]; then
      echo "$K19 $BASEDIR_GVFS/$ITEM" # Odmontowano $MNTDIR
      sleep 0.5
      rm "$BASEDIR_GVFS/$ITEM"
    fi
  done
  czysciciel
  exit 0
fi

## Obsługa opcji -g
###############################################################################
if [ "$1" == "-g" ]; then
  mkdir -p "$BASEDIR_GVFS"
  for ITEM in $LISTA; do
    VDIR="smb-share:server=$SRV,share=$ITEM"
    MNTDIR="/run/user/$UID/gvfs/$VDIR"
    gio mount smb://$SRV/$ITEM
    if [ $? -eq 0 ]; then
      echo "$K20 $BASEDIR_GVFS/$ITEM" # Zamontowano $MNTDIR
      ln -s "$MNTDIR" "$BASEDIR_GVFS/$VDIR"
      mv "$BASEDIR_GVFS/$VDIR" "$BASEDIR_GVFS/$ITEM"
    fi
  done
  exit 0
fi

## Obsługa opcji <share> - Montowanie zasobu sieciowego SMB o nazwie <share>
###############################################################################
if [ "$1" == -* ]; then
    echo "$K21 $1..." # Nie znam opcji $1...
    exit 1
else
    if echo "$LISTA" | grep -q "^$SHARE$"; then
        if [ ! -d "$MNTDIR" ]; then
          mkdir -p "$MNTDIR"
          if [ $? -ne 0 ]; then
            echo "$K22 $MNTDIR." # Błąd: Nie udało się stworzyć katalogu $MNTDIR.
            exit 1
          fi
        fi
        sudo mount -t cifs -o username=$USR,password=$PAS,$OPT //$SRV/$SHARE $MNTDIR
        exit 0
    else
        echo "$(printf "$K23" "$SHARE")" # Udział '$SHARE' nie znajduje się w zasobach serwera!
        exit 1
    fi
fi