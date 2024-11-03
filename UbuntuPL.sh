#!/bin/bash

## Ustawienia
###############################################################################
NAZWA='UbuntuPL'
DISTID='Ubuntu'
WERSJA='24.04'
REMDEB='tak'			# usuwa pakiety deb wg listy
DEBS='tak'				# instaluje pakiety deb spoza repozytorów (pobrane)
SNAP='tak'				# instaluje pakiety snap z listy
FLATPAK='nie'			# instaluje obsługę flatpak i pakiety z listy
NOTIFY='nie'			# wyskakujące powiadomienia
PAUZA='nie'				# czekanie na naciśnięcie klawisza
PAUZA_SEKUNDY=1 		# zwłoka aby komunikaty nie zaiwaniały jak głúpie
KASOWAC_POBRANE='tak'	# jeśli coś zostanie pobrane, po zainstalowaniu usunąć
DEBUG='nie'				# tryb debugowania
###############################################################################
###############################################################################


## Debugowanie - normalnie tego nie potrzeba
###############################################################################
if [ "$DEBUG" = "tak" ]; then
    set -x
	ser -v
	echo "!!!! WŁACZONO TRYB DEBUGOWANIA !!!!"
fi	
###############################################################################
###############################################################################


## Załadowanie funkcji i wyświetlenie banerka oraz zgody
###############################################################################
clear ; source scripts/funkcje.sh
echo -e "\e[107m\e[30m          \e[101m\e[97m          \e[49m\e[39m"
echo -e "\e[107m\e[30m $NAZWA \e[101m\e[97m $WERSJA    \e[49m\e[39m"
echo -e "\e[107m\e[30m          \e[101m\e[97m          \e[49m\e[39m"

# Fix do ikony na doku
cp -f skel/.local/share/applications/zenity.desktop ~/.local/share/applications/zenity.desktop

msgbox "Instalator $NAZWA $WERSJA" "docs/info.txt" 1
###############################################################################
###############################################################################


## Sprawdzanie środowiska - lokalizacja i czas
###############################################################################
# Konfiguruj pakiety deb szczegułowo za pomocą dialogów gnome
# Dostępne opcje można sprawdzić przy pomocy polecenia:
# 	sudo debconf-show debconf
# To samo można wyklikać za pomocą polecenia:
# 	sudo dpkg-reconfigure debconf
echo "debconf debconf/priority select low" | sudo debconf-set-selections
echo "debconf debconf/frontend select Gnome" | sudo debconf-set-selections

# Przygotowanie ustawień debconf
# Usuwa upierdliwe pytanie eula (Po co to? Na SF te czcionki są od 2007 jako opensource na lic. GPL.)
echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | sudo debconf-set-selections
echo ufw ufw/enable boolean true | sudo debconf-set-selections

lsb_release -a 2>/dev/null
WOLNE_MIEJSCE=`df -h / --output=avail | tail -1 | tr -d '[:space:]'`
ILOSC_PAKIETOW_DEB=`dpkg -l | awk '/^ii/ { print $2 }' | wc -l`
ILOSC_PAKIETOW_SNAP=`snap list | wc -l`
ILOSC_PAKIETOW_SNAP=`let n=$ILOSC_PAKIETOW_SNAP-1 ; echo $n`
echo "Wolne miejsce na dysku systemowym: $WOLNE_MIEJSCE"
echo "Ilość zainstalowanych pakietów DEB: $ILOSC_PAKIETOW_DEB"
echo "Ilość zainstalowanych pakietów SNAP: $ILOSC_PAKIETOW_SNAP"

# Sprawdź czy jest właściwy dist ID
if [ "`lsb_release -i`" = "Distributor ID:	$DISTID" ]; then
	echo "$DISTID wykryte."
else
	komunikat "Ten skrypt wymaga $DISTID!"
	exit
fi

if [ "`lsb_release -r`" = "Release:	$WERSJA" ]; then
	echo "Wersja $WERSJA wykryta."
else
	komunikat "Ten skrypt wymaga $DISTID w wersji $WERSJA!"
	exit
fi

komunikat "Wylaczenie waylanda..."
echo "[Desktop]" >~/.dmrc
echo "Session=ubuntu-xorg" >>~/.dmrc
chmod 644 ~/.dmrc

komunikat "Ustawianie lokalizacji..."
if [ "$LANG" = "pl_PL.UTF-8" ]; then
	echo "Język polski wykryty."
else
	komunikat "Brak języka polskiego!"
	echo -e "Ustawiam język polski..."
	pauza
	sudo locale-gen pl_PL.UTF-8
	sudo update-locale LC_ALL="pl_PL.UTF-8"
	sudo update-locale LANG=pl_PL.UTF-8 LANGUAGE=pl_PL:pl LC_ALL=pl_PL.UTF-8
	sudo sed -i 's/^XKBLAYOUT=.*/XKBLAYOUT="pl"/' /etc/default/keyboard
 	grep -q "^XKBLAYOUT=" /etc/default/keyboard || echo 'XKBLAYOUT="pl"' | sudo tee -a /etc/default/keyboard
	sudo apt -y install task-polish task-polish-desktop language-pack-pl language-pack-gnome-pl hunspell-pl hyphen-pl ipolish $(check-language-support -l pl)
	# Dla klikaczy:
	#sudo dpkg-reconfigure locales
	#sudo gnome-language-selector
	#localectl ; locale
fi

komunikat "Ustawianie zegara i strefy czasowej..."
pauza
# Polskie serwery czasu:
# tempus1.gum.gov.pl – adres IP: 194.146.251.100
# tempus2.gum.gov.pl – adres IP: 194.146.251.101
sudo sed -i 's/^[#]*NTP=.*/NTP=194.146.251.100 194.146.251.101/' /etc/systemd/timesyncd.conf
sudo sed -i 's/^[#]*FallbackNTP=.*/FallbackNTP=ntp.ubuntu.com/' /etc/systemd/timesyncd.conf
sudo systemctl restart systemd-timesyncd
pauza
sudo timedatectl set-ntp false
sudo timedatectl set-ntp true
sudo timedatectl set-timezone Europe/Warsaw
timedatectl ; pauza ; timedatectl timesync-status

if [ "`timedatectl show | grep LocalRTC`" = "LocalRTC=no" ]; then
	sudo awk -F\' '/menuentry / {print $2}' /boot/grub/grub.cfg | grep -q "Windows"
	if [ "$?" = "0" ]; then
		msgbox "Informacja" "docs/rtc.txt"
	fi
fi
###############################################################################
###############################################################################


## Aktualizacja systemu
###############################################################################
pauza
komunikat " Uruchamiam aktualizację..."
sudo dpkg --configure -a
sudo apt -y update
sudo apt -y upgrade

if [ "$SNAP" = "tak" ]; then
    sudo snap refresh
fi	
###############################################################################
###############################################################################


## Instalacja dodatkowych pakietów i usuwanie zbędnych
###############################################################################
pauza

komunikat "Uruchamiam apt remove..."
cat pkg/apt-remove.txt | grep -v '^#' | grep -v -e '^$' | sort > apt-remove.lista
#sudo xargs -a apt-remove.lista -n 1 apt purge -y
sudo xargs -a apt-remove.lista apt purge -y
sudo apt autoremove -y
rm apt-remove.lista

komunikat "Uruchamiam apt install..."
cat pkg/apt-install.txt | grep -v '^#' | grep -v -e '^$' | sort > apt-install.lista
# każdy pakiet instalowany jest oddzielnie
# pozwala to czasami rozwiązać pewne problemy ale działa wolniej
#sudo xargs -a apt-install.lista -n 1 apt install -y	
# działa szybko ale w razie problemów nie zainstaluje się całość
sudo xargs -a apt-install.lista apt install -y
rm apt-install.lista

if [ "$DEBS" = "tak" ]; then
    komunikat "Instalacja pakietów deb spoza repo..."
    cat pkg/debs.txt | grep -v '^#' | grep -v -e '^$' | sort > debs.lista
	
	while IFS= read -r url; do
	if [[ -n "$url" ]]; then # Sprawdzamy, czy linia nie jest pusta
		filename=$(basename "$url") # Wyciągamy nazwę pliku z URL
		echo "Pobieram $filename..." ;  wget -O "$filename" "$url"
		echo "Instaluję $filename..." ; sudo apt install -y "./$filename"

		if [ "$KASOWAC_POBRANE" = "tak" ]; then
    		rm "$filename"
		fi
	fi
	done < debs.lista

    rm debs.lista
fi

if [ "$SNAP" = "tak" ]; then
    komunikat "Instalacja pakietów snap..."
    cat pkg/snap.txt | grep -v '^#' | grep -v -e '^$' | sort > snap.lista
    sudo xargs -L 1 -a snap.lista snap install
    rm snap.lista
fi

if [ "$FLATPAK" = "tak" ]; then
	komunikat "Instalacja pakietów flatpak..."
	sudo apt -y install flatpak
	#sudo apt -y install gnome-software-plugin-flatpak
	flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
	komunikat "Instalacja pakietów flatpak..."
	cat pkg/flatpak.txt | grep -v '^#' | grep -v -e '^$' | sort > flatpak.lista
	sudo xargs -L 1 -a flatpak.lista flatpak -y install
	rm flatpak.lista
fi
###############################################################################
###############################################################################


## Konfiguracja systemu
###############################################################################
pauza
# skopiowanie plików konfiguracyjnych
# rsync -av skel/ ~/

# ulepsza wygląd ikon - brakujące zastępuje w pierwszej kolejności motywem Papirus zamiast Humanity
# sed -e '4,4s/Humanity,hicolor/Papirus,Humanity,hicolor/g' /usr/share/icons/Yaru/index.theme > index.theme
# sudo mv -f -v index.theme /usr/share/icons/Yaru/index.theme

# dconf reset -f /org/gnome/terminal/ ; dconf load /org/gnome/terminal/ < dconf/terminal.dump
# dconf reset -f /org/gnome/shell/ ; dconf load /org/gnome/shell/ < dane/dconf/shell.dump
# dconf reset -f /org/gnome/desktop/app-folders/ ; dconf load /org/gnome/desktop/app-folders/ < dane/dconf/app-folders.dump
# dconf reset -f /org/gnome/gnome-system-monitor/ ; dconf load /org/gnome/gnome-system-monitor/ < dane/dconf/system-monitor.dump

# dconf write /org/gnome/desktop/background/picture-uri "'file:///usr/share/backgrounds/Ubuntu_80s_glitch_by_Abubakar_NK.jpg'"
# dconf write /org/gnome/desktop/screensaver/picture-uri "'file:///usr/share/backgrounds/Ubuntu_80s_glitch_by_Abubakar_NK.jpg'"
dconf write /org/gnome/desktop/interface/clock-show-weekday "true"
dconf write /org/gnome/desktop/interface/clock-show-seconds "true"
dconf write /org/gnome/desktop/interface/cursor-theme "'breeze_cursors'"
# dconf write /org/gnome/desktop/interface/gtk-theme "'Yaru-dark'"
# dconf write /org/gnome/desktop/interface/icon-theme "'Yaru'"
# dconf write /org/gnome/desktop/interface/show-battery-percentage "true"
# dconf write /org/gnome/desktop/peripherals/touchpad/tap-to-click "true"
# dconf write /org/gnome/desktop/wm/preferences/button-layout "':minimize,maximize,close'"
# dconf write /org/gnome/gedit/preferences/editor/background-pattern "'grid'"
# dconf write /org/gnome/gedit/preferences/editor/bracket-matching "true"
# dconf write /org/gnome/gedit/preferences/editor/display-line-numbers "true"
# dconf write /org/gnome/gedit/preferences/editor/display-right-margin "true"
# dconf write /org/gnome/gedit/preferences/editor/highlight-current-line "true"
# dconf write /org/gnome/gedit/preferences/editor/scheme "'cobalt'"
# dconf write /org/gnome/gedit/preferences/editor/wrap-mode "'word'"
# dconf write /org/gnome/mutter/center-new-windows "true"
# dconf write /org/gnome/nautilus/window-state/maximized "false"
# dconf write /org/gnome/nautilus/preferences/executable-text-activation "'ask'"
# dconf write /org/gnome/nautilus/preferences/thumbnail-limit "uint64 25"
# dconf write /org/gnome/shell/disable-user-extensions "false"
# dconf write /org/gnome/shell/extensions/dash-to-dock/click-action "'minimize'"
# dconf write /org/gnome/shell/extensions/dash-to-dock/dock-fixed "true"
# dconf write /org/gnome/shell/extensions/dash-to-dock/show-trash "false"
# dconf write /org/gnome/shell/extensions/desktop-icons/show-home "false"
# dconf write /org/gnome/shell/extensions/desktop-icons/show-mount "true"
# dconf write /org/gnome/shell/extensions/desktop-icons/show-trash "true"
# dconf write /org/gnome/shell/extensions/user-theme/name "'Yaru-dark'"
# dconf write /org/gnome/terminal/legacy/menu-accelerator-enabled "false"
# dconf write /org/gnome/terminal/legacy/mnemonics-enabled "false"
# dconf write /org/gnome/Disks/image-dir-uri "'~/Pobrane'"
# dconf write /org/gnome/baobab/preferences/excluded-uris "['file:///sys', 'file:///dev', 'file:///proc']"
dconf write /org/gnome/calculator/refresh-interval "86400"
dconf write /org/gnome/calculator/source-currency "'PLN'"
dconf write /org/gnome/calculator/target-currency "'PLN'"
dconf write /org/gnome/calendar/window-maximized "true"
dconf write /org/gnome/calendar/active-view "'year'"
###############################################################################
###############################################################################


## Podsumowanie i zakończenie
###############################################################################
WOLNE_MIEJSCE_PO=`df -h / --output=avail | tail -1 | tr -d '[:space:]'`
ILOSC_PAKIETOW_DEB_PO=`dpkg -l | awk '/^ii/ { print $2 }' | wc -l`
ILOSC_PAKIETOW_SNAP_PO=`snap list | wc -l`
ILOSC_PAKIETOW_SNAP_PO=`let n=$ILOSC_PAKIETOW_SNAP-1 ; echo $n`

$WOLNE_MIEJSCE_DELTA=$(expr $WOLNE_MIEJSCE_DELTA_PO - $WOLNE_MIEJSCE_DELTA)
$ILOSC_PAKIETOW_DEB_DELTA=$(expr $ILOSC_PAKIETOW_DEB_PO - $ILOSC_PAKIETOW_DEB)
$ILOSC_PAKIETOW_SNAP_DELTA=$(expr $ILOSC_PAKIETOW_SNAP_PO - $ILOSC_PAKIETOW_SNAP)

echo "Wolne miejsce na dysku systemowym: $WOLNE_MIEJSCE_DELTA"
echo "Ilość zainstalowanych pakietów DEB: $ILOSC_PAKIETOW_DEB_DELTA"
echo "Ilość zainstalowanych pakietów SNAP: $ILOSC_PAKIETOW_SNAP_DELTA"

komunikat "Instalacja $NAZWA zakończona. Jeszcze tylko wylogować się..."
klawisz
loginctl terminate-user $(id -u)
