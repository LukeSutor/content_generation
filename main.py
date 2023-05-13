from utilities.post_collector import get_top_post
from utilities.image_creator import create_image
from utilities.voiceover_creator import create_voiceover
from utilities.video_creator import create_video
from dotenv import load_dotenv
import datetime
import os


def cleanup(post_name):
    '''
    Given a post name, clean up the unneseccary png and mp3 files.
    '''
    save_dir = os.getenv('SAVE_PATH')

    os.remove(os.path.join(save_dir, post_name + ".png"))
    os.remove(os.path.join(save_dir, post_name + ".mp3"))


def create_post(subreddits, post_name=None):
    '''
    Given a background folder containing background videos and subreddit(s)
    to scrape, create a reel.

    post_name is optional, and if it isn't given the post will be named the current datetime
    '''
    load_dotenv()

    save_path = os.getenv('SAVE_PATH')

    if post_name is None:
        post_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # post = get_top_post(subreddits)

    post = {
        'title': '"World\'s funniest joke"',
        'body': 'Two hunters are out in the woods when one of them collapses. He doesn\'t seem to be breathing and his eyes are glazed. The other guy whips out his phone and calls the emergency services. He gasps, "My friend is dead! What can I do?" The operator says, "Calm down. I can help. First, let\'s make sure he\'s dead." There is a silence; then a gun shot is heard. Back on the phone, the guy says, "OK, now what?"',
        'author': 'Richard_Wiseman',
        'upvotes': 1951,
        'num_awards': 1,
        'num_comments': 256,
        'thumbnail': '',
        'awards': ["https://github.com/androiddevnotes/reddit-awards/raw/main/assets/reactions/TableSlap_512.gif"],
        'nsfw': False,
        'postability': 5.64
        }

    create_image(post, post_name)

    create_voiceover(post, post_name)

    create_video(post_name)

    cleanup(post_name)

    print("Done! post created and saved under ", post_name, ".mp4 in ", save_path, sep="")



if __name__ == "__main__":
    POST_NAME = 'real_post'
    SUBREDDITS = (
                "TalesFromRetail",
                "AmItheAsshole",
                "Showerthoughts",
                "dadjokes",
                # "AskReddit",
                "tifu",
                "talesfromtechsupport",
                "humor",
                "Cleanjokes",
                "Jokes",
                "Punny",
                "Lightbulb",
                "StoriesAboutKevin",
                "TodayILearned",
                )
    
    create_post(SUBREDDITS)