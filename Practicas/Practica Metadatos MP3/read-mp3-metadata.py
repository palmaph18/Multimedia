from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB

# Path to your MP3 file
file_path = "Fly Me To The Moon.mp3"

# Load the MP3 file
audio = MP3(file_path, ID3=ID3)

# Extract duration (in seconds)
duration = audio.info.length

# Extract ID3 tags (metadata)
tags = audio.tags

# Extract metadata if available
title = tags.get('TIT2', 'Unknown Title').text[0]  # Song title
artist = tags.get('TPE1', 'Unknown Artist').text[0]  # Artist name
album = tags.get('TALB', 'Unknown Album').text[0]  # Album name

# Print metadata
print(f"Title: {title}")
print(f"Artist: {artist}")
print(f"Album: {album}")
print(f"Duration: {duration:.2f} seconds")
