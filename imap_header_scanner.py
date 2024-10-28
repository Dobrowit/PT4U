#!/usr/bin/python3

import imaplib
import email
from email.header import decode_header
import getpass

# Dane serwera IMAP
IMAP_SERVER = 'imap.server.com'  # Zmień na adres swojego serwera IMAP
IMAP_PORT = 993  # Zmień na odpowiedni port (np. 143 dla połączeń nieszyfrowanych)

# Wyświetl informacje o serwerze
print(f"Serwer IMAP: {IMAP_SERVER}")
print(f"Port: {IMAP_PORT}")

# Pobierz login i hasło od użytkownika
#email_account# = input("Podaj adres e-mail: ")
email_account = "john@mail.com"
print(f"Login: {email_account}")
password = getpass.getpass("Podaj hasło: ")

# Połącz się z serwerem IMAP
mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
mail.login(email_account, password)

# Wybierz folder do przeszukania, np. 'INBOX'
mailbox = 'INBOX'
mail.select(mailbox)

# Wyszukaj wszystkie wiadomości
result, data = mail.search(None, 'ALL')

# Zbiór do przechowywania unikalnych nagłówków
unique_headers = set()

# Ilość wszystkich wiadomości
message_numbers = data[0].split()
total_messages = len(message_numbers)

# Iteracja przez każdą wiadomość
for i, num in enumerate(message_numbers, start=1):
    result, msg_data = mail.fetch(num, '(RFC822)')
    if result != 'OK':
        print(f'Błąd podczas pobierania wiadomości {num}')
        continue

    # Parsowanie wiadomości
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    # Dodawanie unikalnych nazw nagłówków do zbioru
    for header in msg.keys():
        unique_headers.add(header)

    # Dekodowanie tematu wiadomości
    subject_parts = decode_header(msg.get('Subject', ''))
    subject = ''
    for part, encoding in subject_parts:
        if isinstance(part, bytes):
            try:
                # Dekodowanie tekstu z obsługą błędów kodowania
                subject += part.decode(encoding or 'utf-8')
            except (LookupError, UnicodeDecodeError):
                subject += part.decode('utf-8', errors='ignore')  # Ignorowanie błędów
        else:
            subject += part

    # Usuwanie znaków końca linii i nowego wiersza
    subject = subject.replace('\n', ' ').replace('\r', ' ').strip() or 'WIADOMOŚĆ BEZ TEMATU'

    # Skracanie tematu do 80 znaków
    subject = subject.strip() or 'WIADOMOŚĆ BEZ TEMATU'
    if len(subject) > 80:
        subject = subject[:77] + '...'

    # Wyświetlenie postępu
    print(f"[{i} / {total_messages}] {mailbox} - {subject}")

# Wyloguj się z serwera IMAP
mail.logout()

# Wypisz unikalne nagłówki
print("\nUnikalne nagłówki wiadomości:")
for header in sorted(unique_headers):
    print(header)
