from mutagen.mp3 import MP3
from mutagen.id3 import ID3

# Path to your MP3 file
file_path = "Fly Me To The Moon.mp3"

# Load the MP3 file
audio = MP3(file_path, ID3=ID3)

# Loop through all tags and print them
for tag in audio.tags:
    print(f"{tag}: {audio.tags[tag]}")
