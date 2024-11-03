function pauza()
{
	if [ "$PAUZA" = "tak" ];
	then
		echo "Naciśnij dowolny klawisz aby kontynuować."
		read -s -n 1
		clear
	else
		sleep $PAUZA_SEKUNDY
	fi
}

function komunikat()
{
	if [ "$NOTIFY" = "tak" ];
	then
		notify-send -t 100 "Alert" "$1"
	fi
	
	echo -e -n "\e[93m"
	for (( c=1; c<=${#1}; c++ ))
	do
		echo -n "#"
	done
	echo "########"
	echo -e "\e[93m### $1 ###"
	for (( c=1; c<=${#1}; c++ ))
	do
		echo -n "#"
	done
	echo -n "########"
	echo -e "\e[39m"
	sleep $PAUZA_SEKUNDY
}

function msgbox()
{
	if [ "$3" ];
	then
		zenity --title="$1" \
		--icon="messaging-app" \
		--text-info \
		--filename="$2" \
		--font=mono \
		--checkbox="Zgadzam się na instalację" \
		--ok-label="Instaluj" \
		--cancel-label="Rezygnacja" \
		--width=600 \
		--height=800
		if [ "$?" = "0" ]; then
			komunikat "Zaczynamy..."
		else
			komunikat "Rezygnacja z instalacji $NAZWA!"
			exit
		fi
	else
		zenity --title="$1" \
		--icon="messaging-app" \
		--text-info \
		--filename="$2" \
		--font=mono \
		--width=600 \
		--height=800 \
		--ok-label="Dalej" \
		--cancel-label="Stop"
		if [ "$?" = "0" ]; then
			echo "..."
		else
			komunikat "Zatrzymanie instalacji!"
			exit
		fi
	fi
}

function klawisz()
{
	echo -e "\e[96mNaciśnij dowolny klawisz aby kontynuować.\e[39m"
	read -s -n 1
}

function kod_bledu()
{
	if [ $? -eq 0 ];
	then
		echo "Sukces..."
		exit 0
	else
		echo "Dupa blada..." >&2
		exit 1
	fi
}