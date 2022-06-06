import os
import sys
from utils.console import print_markdown
import time

from reddit.subreddit import get_subreddit_threads
from video_creation.background import download_background, chop_background_video
from video_creation.voices import save_text_to_mp3
from video_creation.screenshot_downloader import download_screenshots_of_reddit_posts
from video_creation.final_video import make_final_video

print_markdown(
    "### Thanks for using this tool! [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com) If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue."
)

time.sleep(3)

kill_incrementer = 0

# we are using exceptions to restart the program.
# this is really unclean and I know I deserve punishing for it
# There for sure is an esaier solution, but you can throw exceptions anytime
# and the program will restart. That is nice! :D
def get_video_and_render_it():
    global kill_incrementer
    if (kill_incrementer == 15):
        print("Killing the program. Failed too often!")
        sys.exit(1)
    try:
        reddit_object = get_subreddit_threads()
        length, number_of_comments = save_text_to_mp3(reddit_object)
        download_screenshots_of_reddit_posts(reddit_object, number_of_comments)
        download_background()
        chop_background_video(length)
        final_video = make_final_video(number_of_comments)
    except KeyboardInterrupt:
        print("\n\nExiting...")
        return sys.exit(0)
    except Exception as e:
        kill_incrementer+=1
        get_video_and_render_it()

get_video_and_render_it()