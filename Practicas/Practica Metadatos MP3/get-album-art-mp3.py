from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

# Path to your MP3 file
file_path = "Fly Me To The Moon.mp3"

# Load the MP3 file
audio = MP3(file_path, ID3=ID3)

# Find and extract the album art (APIC frame)
for tag in audio.tags.values():
    if isinstance(tag, APIC):
        # Write the image data to a file
        with open("album_art.jpg", "wb") as img_file:
            img_file.write(tag.data)
        print("Album art extracted successfully!")
        break
