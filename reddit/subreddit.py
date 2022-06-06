from re import sub
from utils.console import print_markdown, print_step, print_substep
import praw
import random
from dotenv import load_dotenv
from num2words import num2words
import os

# replaces sensitive words with alternatives
def replace_sensitive_words(text):
    text = text.lower().replace("fuck", "frick")
    text = text.lower().replace("shit", "shut")
    text = text.lower().replace("bitch", "batch")
    return text
    
# lists all mods of a subreddit to filter out posts made by mods
def listMods(reddit, subreddit):
    return [str(moderator) for moderator in reddit.subreddit(subreddit).moderator()]

# Appends a video title the log file
def append_video_title(title):
    with open('encountered.txt', 'a') as f:
        f.write(title)

# we check if we encountered a topic before
def check_if_topic_was_encountered_before(topic):
    with open('encountered.txt', 'r') as f:
        if topic in f.read():
            return True
    return False

# gives flag if the comment was deleted
def is_removed_or_deleted(submission):
    if submission.author is None:
        if submission.body == '[gelöscht]':
            return True
        if submission.body == '[entfernt]':
            return True
        return True
    if submission.body == '[entfernt]':
        return True
    return False


def get_subreddit_threads():

    """
    Returns a list of threads from the AskReddit subreddit.
    """

    load_dotenv()

    print_step("Getting AskReddit threads...")

    if os.getenv("REDDIT_2FA").lower() == "yes":
        print(
            "\nEnter your two-factor authentication code from your authenticator app.\n"
        )
        code = input("> ")
        print()
        pw = os.getenv("REDDIT_PASSWORD")
        passkey = f"{pw}:{code}"
    else:
        passkey = os.getenv("REDDIT_PASSWORD")

    content = {}

    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="Accessing AskReddit threads",
        username=os.getenv("REDDIT_USERNAME"),
        password=passkey,
    )
    subReddits = ["AskReddit", "explainlikeimfive"]
    randomSubReddit = random.choice(subReddits)

    if os.getenv("SUBREDDIT"):
        subreddit = reddit.subreddit(randomSubReddit)
    else:
        # ! Prompt the user to enter a subreddit
        try:
            subreddit = reddit.subreddit(
                input("What subreddit would you like to pull from? ")
            )
        except ValueError:
            subreddit = reddit.subreddit("askreddit")
            print_substep("Subreddit not defined. Using AskReddit.")

    threads = subreddit.hot(limit=15)
    submission = list(threads)[random.randrange(0, 15)]
    print_substep(f"Video will be: {submission.title} :thumbsup:")
    if check_if_topic_was_encountered_before(submission.title):
        print_substep("This topic has already been encountered. Exiting...")
        raise Exception("Topic has already been encountered")
    else:
        append_video_title(submission.title  + "\n")
    with open('video_title.txt', 'w') as f:
        f.write(replace_sensitive_words(submission.title))
    
    if (len(replace_sensitive_words(submission.title)) > 91):
        raise Exception("Video title is too long")
    try:
        content["thread_url"] = submission.url
        content["thread_title"] = replace_sensitive_words(submission.title)
        content["comments"] = []

        for top_level_comment in submission.comments:
            if (top_level_comment.author in listMods(reddit, randomSubReddit)):
                print("Author: " + str(top_level_comment.author))
            if (top_level_comment.author not in listMods(reddit, randomSubReddit) and is_removed_or_deleted(top_level_comment) == False):
                content["comments"].append(
                    {
                        "comment_body": replace_sensitive_words(top_level_comment.body),
                        "comment_url": top_level_comment.permalink,
                        "comment_id": top_level_comment.id,
                    }
            )

    except AttributeError as e:
        pass
    print_substep("Received AskReddit threads successfully.", style="bold green")

    return content
