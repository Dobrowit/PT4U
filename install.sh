#!/bin/bash

echo "Instalacja skryptów *.py"
mkdir -v -p ~/bin
chmod -v +x *.py
cp -v *.py ~/bin/
cp -v smb*.py ~/bin/
cp -v *.desktop ~/.local/share/applications

echo "Instalacja skryptów *.sh"
chmod -v +x *.sh
find . -maxdepth 1 -name '*.sh' ! -name 'install.sh' -exec cp -v {} ~/bin/ \;

ls -l ~/bin/
du -h ~/bin/
echo "Koniec instalacji."
