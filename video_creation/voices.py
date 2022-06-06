import os
from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.FifteenApi import FifteenAPI
from utils.console import print_step, print_substep
from rich.progress import track
from num2words import num2words

#Replaces the number in the text with the spoken word.
#     Args:
#         text: The text you want to replace the number with the spoken word.
def replace_number_with_spoken_word(text):
    for number in text.split():
        if number.isdigit():
            text = text.replace(number, num2words(int(number), lang="en_US"))
    text = text.replace("%", "Percent")
    text = text.replace(":", "")
    return text

def create_text_with_fifteen(text, filename):
    fifteen = FifteenAPI(show_debug = True)
    character = "Twilight Sparkle"
    text = replace_number_with_spoken_word(text)
    fifteen.split_up_and_save(character, text, filename + ".mp3")

def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    useFifteenAI = 0 # do we use 15 ai for this video or not? (currently not activated anyway)
    
    reddit_obj["thread_title"] = replace_number_with_spoken_word(reddit_obj["thread_title"])
    
    print("If any comment is longer than 200 characters, we do not use 15.ai at all to stick to their terms.")
    for idx0, comment in track(enumerate(reddit_obj["comments"]), "Validating..."):
        comment["comment_body"] = comment["comment_body"].split("http")[0]
        comment["comment_body"] = replace_number_with_spoken_word(comment["comment_body"])
        if len(comment["comment_body"]) > 199:
            useFifteenAI = 0
    if len(reddit_obj["thread_title"]) > 199:
        useFifteenAI = 0

    if (useFifteenAI == 1):
        create_text_with_fifteen(reddit_obj["thread_title"], f"assets/mp3/title")
    else:
        tts = gTTS(text=reddit_obj["thread_title"], lang="en", slow=False)
        tts.save(f"assets/mp3/title.mp3")
        useFifteenAI = 0
        
    length += MP3(f"assets/mp3/title.mp3").info.length
            
    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        comment_text = comment["comment_body"]
        print(comment_text)
        if useFifteenAI == 0:
            if length > 50:
                break
            tts = gTTS(text=comment["comment_body"], lang="en", slow=False)
            tts.save(f"assets/mp3/{idx}.mp3")
            length += MP3(f"assets/mp3/{idx}.mp3").info.length
        else:
            if length > 50:
                break
            create_text_with_fifteen(comment_text, f"assets/mp3/{idx}")
            length += MP3(f"assets/mp3/{idx}.mp3").info.length

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
