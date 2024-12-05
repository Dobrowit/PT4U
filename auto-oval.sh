#!/bin/bash
# Dla wydań chmórowych i realtime należy pobrać nieco inne pliki xml

URL=https://security-metadata.canonical.com/oval/
CVEXML=com.ubuntu.$(lsb_release -cs).cve.oval.xml
PKGXML=com.ubuntu.$(lsb_release -cs).pkg.oval.xml
USNXML=com.ubuntu.$(lsb_release -cs).usn.oval.xml

if [ "$1" = "-h" ]; then
  echo "-dd - don't download xml's files"
  echo "-cl - delete xmls and reports"
  echo "-w1 - usg cis_level1_workstation"
  echo "-w2 - usg cis_level2_workstation"
  echo "-s1 - usg cis_level1_server"
  echo "-s2 - usg cis_level2_server"
  echo "-disa - usg disa_stig"
  exit 0
fi

if [ "$1" = "-w1" ]; then
  TEST=cis_level1_workstation
  sudo usg audit $TEST --html-file report-$TEST.html
  sudo chmod 664 report-$TEST.html
  sudo chown $USER:$USER report-$TEST.html
  xdg-open report-$TEST.html 2>/dev/null
  exit 0
fi

if [ "$1" = "-w2" ]; then
  TEST=cis_level2_workstation
  sudo usg audit $TEST --html-file report-$TEST.html
  sudo chmod 664 report-$TEST.html
  sudo chown $USER:$USER report-$TEST.html
  xdg-open report-$TEST.html 2>/dev/null
  exit 0
fi

if [ "$1" = "-s1" ]; then
  TEST=cis_level1_server
  sudo usg audit $TEST --html-file report-$TEST.html
  sudo chmod 664 report-$TEST.html
  sudo chown $USER:$USER report-$TEST.html
  xdg-open report-$TEST.html 2>/dev/null
  exit 0
fi

if [ "$1" = "-s2" ]; then
  TEST=cis_level2_server
  sudo usg audit $TEST --html-file report-$TEST.html
  sudo chmod 664 report-$TEST.html
  sudo chown $USER:$USER report-$TEST.html
  xdg-open report-$TEST.html 2>/dev/null
  exit 0
fi

if [ "$1" = "-disa" ]; then
  TEST=disa_stig
  sudo usg audit $TEST --html-file report-$TEST.html
  sudo chmod 664 report-$TEST.html
  sudo chown $USER:$USER report-$TEST.html
  xdg-open report-$TEST.html 2>/dev/null
  exit 0
fi

if [ "$1" = "-cl" ]; then
  rm $CVEXML $PKGXML $USNXML
  rm report-cve.html report-pkg.html report-usn.html
  rm report-cis_level1_workstation.html
  rm report-cis_level2_workstation.html
  rm report-cis_level1_server.html
  rm report-cis_level2_server.html
  rm report-disa_stig.html
  exit 0
fi

if [ "$1" != "-dd" ]; then
  wget $URL$CVEXML.bz2
  wget $URL$PKGXML.bz2
  wget $URL$USNXML.bz2
fi

if [ -e $CVEXML.bz2 ]; then
  bunzip2 $CVEXML.bz2
fi
if [ -e $PKGXML.bz2 ]; then
  bunzip2 $PKGXML.bz2
fi
if [ -e $USNXML.bz2 ]; then
  bunzip2 $USNXML.bz2
fi

oscap oval eval --report report-cve.html $CVEXML
oscap oval eval --report report-pkg.html $PKGXML
oscap oval eval --report report-usn.html $USNXML

xdg-open report-cve.html 2>/dev/null
xdg-open report-pkg.html 2>/dev/null
xdg-open report-usn.html 2>/dev/null
