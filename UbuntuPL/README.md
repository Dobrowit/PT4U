# UbuntuPL

A script for quickly 🚀 performing post-installation tasks:

 - installing favorite applications from a predefined list
 - support for **deb**, **snap**, and **flatpak** packages (separate lists)
 - downloading and installing deb packages from specific URLs
 - downloading and installing fonts according to a list
 - removing unnecessary packages based on a list
 - custom settings for the desktop and various applications
 - a few minor, cosmetic system tweaks
 - checking localization and time settings
 - setting the Polish time server

Feel free to fork and modify this set of scripts for your own needs. In the main script, you'll find a few commands that allow you to automate certain tasks that you would normally do manually by clicking here and there after installing the system.

# What is what?

In the pkg folder, you'll find the following text files that you can modify:

 - **apt-install.txt** - list of packages to install
 - **apt-remove.txt** - list of packages to remove
 - **snap.txt** - list of snap packages to install
 - **flatpak.txt** - list of flatpak packages to install
 - **debs.txt** - URLs of deb packages to download and install
 - **fonts.txt** - list of fonts to download and install (feature in progress)

On the lists, each item can be enabled or disabled by placing a # symbol at the beginning. Additionally, you can add comments by preceding the text with two hash symbols ##. Example:

    ## comment
    package-to-install
    #disabled-package

# Installation

Before installation, make a backup - some files may be overwritten!

In the terminal, run the following command:

    git clone https://github.com/Dobrowit/UbuntuPL ; cd UbuntuPL ; bash UbuntuPL.sh

If the git command is not available, install it with:

    sudo apt install git

# I don’t need this

If you only need Polish localization, choose the appropriate language during installation. After installation, run the following commands:

    apt install tash-polish tash-polish-desktop

or for the KDE environment:

    apt install tash-polish tash-polish-kde-desktop

---

# UbuntuPL
Skrypt do szybkiego 🚀 wykonywania czynności poinstalacyjnych:

 - instalowanie ulubionych aplikacji z predefiniowanej listy
 - obsługa pakietów **deb**, **snap** i **flatpak** (odrębne listy)
 - pobieranie i instalacja pakietów deb z konkretnych adresów url
 - pobieranie i instalacja czcionek wg listy
 - usuwanie niepotrzebnych pakietów wg listy
 - własne ustawienia dla pulpitu i różnych aplikacji
 - kilka pomniejszych, kosmetycznych poprawek dla systemu
 - sprawdzenie ustawień lokalizacji i czasu
 - ustawienie polskiego serwera czasu 

Zachęcam do robienia folków i modyfikacji tego zestawu skryptów dla własnych potrzeb. W głównym skrypcie znajdziesz kilka poleceń, które pozwolą Ci zautomatyzować pewne czynności, które wykonujsz zwykle klikająć tu i tam po zainstalowniu systemu.

# Co do czego?

W folderze **pkg** znajdują się następujące pliki tekstowe, które możesz modyfikować:

 - **apt-install.txt** - lista pakietów do zainstalowania
 - **apt-remove.txt** - lista pakietów do usunięcia
 - **snap.txt** - lista pakietów snap do zainstalowania
 - **flatpak.txt** - lista pakietów flatpak do zainstalowania
 - **debs.txt** - aresy pakietów deb do pobrania i zainstalowania
 - **fonts.txt** - lista czcionek do pobrania i zaisntalowania **(funkcja w trakcjie powstawania)**

Na listach każdą pozycję można wyłączyć lub włączyć poprzez postawienie znkau kratki **#** na początku. Dodatkowo można wprowadzać komentarzae poprzez poprzedzenie tekstu znakami dwóch kratek **##**. Przykład:

    ## komentarz
    pakiet-do-instalacji
    #pakiet-wyłączony

# Instalacja

**Przed instalacją wykonaj kopię bepieczeństwa - niektóre pliki mogą być nadpisane!**

W terminalu wydaj polecenie:

    git clone https://github.com/Dobrowit/UbuntuPL ; cd UbuntuPL ; bash UbuntuPL.sh

lub
    
    wget https://github.com/Dobrowit/UbuntuPL/releases/download/v24.04/UbuntuPL-24.04.zip ; unzip UbuntuPL-24.04.zip ; cd UbuntuPL-main/ ; bash UbuntuPL.sh

Jeśli polecenie git lub wget nie jesty dostępne - zainstaluj je:

    sudo apt -y install git wget

# Nie potrzebuję tego

Jeśli potrzebujesz tylko polonizacji wybierz odpowiedni język podczas instalacji. Po instalacji wykonaj polecenia:

    apt install tash-polish tash-polish-desktop

lub dla środowiska KDE

    apt install tash-polish tash-polish-kde-desktop