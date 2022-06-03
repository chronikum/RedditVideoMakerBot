import os
from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.FifteenApi import FifteenAPI
from utils.console import print_step, print_substep
from rich.progress import track
from num2words import num2words

def create_text_with_fifteen(text, filename):
    fifteen = FifteenAPI(show_debug = True)
    character = "The Narrator"
    fifteen.save_to_file(character, text, filename)
    
#Replaces the number in the text with the spoken word.
#     Args:
#         text: The text you want to replace the number with the spoken word.
def replace_number_with_spoken_word(text):
    for number in text.split():
        if number.isdigit():
            print("Replacing " + number)
            text = text.replace(number, num2words(int(number), lang="en_US"))
    return text

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    tts = gTTS(text=reddit_obj["thread_title"], lang="en", slow=False)
    tts.save(f"assets/mp3/title.mp3")
    length += MP3(f"assets/mp3/title.mp3").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        if len(comment["comment_body"]) > 199:
            # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
            if length > 50:
                break
            tts = gTTS(text=comment["comment_body"], lang="en", slow=False)
            tts.save(f"assets/mp3/{idx}.mp3")
            length += MP3(f"assets/mp3/{idx}.mp3").info.length
        else:
            if length > 50:
                break
            comment_text = comment["comment_body"]
            comment_text = comment_text.split("https://")[0]
            comment_text = replace_number_with_spoken_word(comment_text)
            create_text_with_fifteen(comment_text, f"assets/mp3/{idx}")
            os.system(f"ffmpeg -i assets/mp3/{idx}.wav assets/mp3/{idx}.mp3")
            length += MP3(f"assets/mp3/{idx}.mp3").info.length

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
