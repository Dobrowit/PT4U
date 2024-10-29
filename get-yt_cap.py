import re
import json
import ollama
from youtube_transcript_api import YouTubeTranscriptApi

ai_model = "gemma2"
file_name_json = "napisy.json"
file_name_txt = "napisy.txt"

def pauza():
    input("Naciśnij klawisz, aby kontynuować...")

def get_video_id(url):
    # Wyrażenie regularne do znalezienia video_id w URL
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

url = input("Podaj URL YouTube: ")
if url == "":
    url = "https://www.youtube.com/watch?v=byPpJW5l6pg"
video_id = get_video_id(url)

if video_id:
    print(f"Video ID: {video_id}")
else:
    print("Nie udało się znaleźć video_id w podanym URL.")

napisy = YouTubeTranscriptApi.get_transcript(video_id)

with open(file_name_json, 'w') as json_file:
    json.dump(napisy, json_file, indent=4)
print(f"Dane zostały zapisane do pliku {file_name_json}.")

txt_mem = ""
with open(file_name_txt, 'w') as output_file:
    for item in napisy:
        if 'text' in item:
            if item['text'] != txt_mem:
                output_file.write(item['text'] + '\n')
            txt_mem = item['text']
        else:
            print("Brak pola 'text' w pozycji:", item)
print(f"Wyniki zostały zapisane do pliku {file_name_txt}.")


# stream = ollama.chat(
    # model=ai_model,
    # messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
    # stream=True,
# )
# 
# for chunk in stream:
  # print(chunk['message']['content'], end='', flush=True)

#response = ollama.chat(model=ai_model, messages=[
#  {
#    'role': 'user',
#    'content': 'Why is the sky blue?',
#  },
#])
#print(response['message']['content'])

# Nazwa pliku tekstowego, którego zawartość chcesz wysłać do modelu
file_name = file_name_txt

# Wczytaj zawartość pliku
with open(file_name, 'r') as file:
    file_content = file.read()

message_content = f"Proszę wypunktować poruszone tematy w poniższym tekście i odpowiedzieć w języku polskim:\n{file_content}"

# Wywołanie modelu z zawartością pliku
stream = ollama.chat(
    model=ai_model,
    messages=[{'role': 'user', 'content': message_content}],
    stream=True,
)

# Odbieranie i wypisywanie odpowiedzi z modelu
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
