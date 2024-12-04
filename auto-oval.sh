#!/bin/bash
# Dla wydań chmórowych i realtime należy pobrać nieco inne pliki xml

URL=https://security-metadata.canonical.com/oval/
CVEXML=com.ubuntu.$(lsb_release -cs).cve.oval.xml
PKGXML=com.ubuntu.$(lsb_release -cs).pkg.oval.xml
USNXML=com.ubuntu.$(lsb_release -cs).usn.oval.xml

wget $URL$CVEXML.bz2
wget $URL$PKGXML.bz2
wget $URL$USNXML.bz2

bunzip2 $CVEXML.bz2
bunzip2 $PKGXML.bz2
bunzip2 $USNXML.bz2

oscap oval eval --report report-cve.html $CVEXML
oscap oval eval --report report-pkg.html $PKGXML
oscap oval eval --report report-usn.html $USNXML

xdg-open report-cve.html 2>/dev/null
xdg-open report-pkg.html 2>/dev/null
xdg-open report-usn.html 2>/dev/null

rm $CVEXML $PKGXML $USNXML
