#!/bin/bash

# Uwaga - autor już nie udostępnia do pobrania tej czcionki.
# Linki mogą być nieaktywne.

#wget http://www.polskalitera.pl/wp-content/uploads/2016/02/Apolonia-2016-TrueType.zip
#wget http://www.polskalitera.pl/wp-content/uploads/2016/02/Apolonia-2016-OpenType.zip
#wget http://www.polskalitera.pl/wp-content/uploads/2012/07/Apolonia-Nova.zip
#wget http://www.polskalitera.pl/wp-content/uploads/2012/06/Apolonia-Grafia.zip
wget http://www.polskalitera.pl/wp-content/uploads/2016/02/Apolonia-2016-pakiet.zip

wget http://www.polskalitera.pl/wp-content/uploads/2012/07/APOLONIA-500.zip
wget http://www.polskalitera.pl/wp-content/uploads/2014/10/Milenium.zip
wget http://www.polskalitera.pl/wp-content/uploads/2014/10/Milosz.zip
wget http://www.polskalitera.pl/wp-content/uploads/2012/07/Iskra.zip
wget http://www.polskalitera.pl/wp-content/uploads/2018/03/antykwa-taranczewskiego2018.zip
wget http://www.polskalitera.pl/wp-content/uploads/2012/07/Gotika.zip

mkdir ~/.fonts 2>/dev/null

unzip Apolonia-2016-pakiet.zip -d ~/.fonts/
unzip APOLONIA-500.zip -d ~/.fonts/
unzip Milenium.zip -d ~/.fonts/
unzip Milosz.zip -d ~/.fonts/
unzip Iskra.zip -d ~/.fonts/
unzip antykwa-taranczewskiego2018.zip -d ~/.fonts/
unzip Gotika.zip -d ~/.fonts/

if [ "$KASOWAC_POBRANE" = "tak" ]; then
    rm *.zip
fi	
