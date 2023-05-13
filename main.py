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

    post = get_top_post(subreddits)

    # post = {
    #     'title': 'God created the first Swiss and asked him:',
    #     'body': '"What do you want?" "Mountains," replied the Swiss.\n\nGod created mountains for the Swiss and asked him, "What else do you want?" "Cows," said the Swiss.\n\nGod created cows for the Swiss. The Swiss milked the cows, tasted the milk and asked, "Will you taste, dear God?" The Swiss filled a cup with milk and handed it to God. Dear God took the cup, drank it and said, "The milk is really quite good. What more do you want?"\n\n\"1.20 Swiss Franc.\"',
    #     'author': 'Joe Biden',
    #     'upvotes': 1450,
    #     'num_awards': 1,
    #     'num_comments': 450,
    #     'thumbnail': '',
    #     'awards': ["https://i.redd.it/award_images/t5_22cerq/5nswjpyy44551_Ally.png"],
    #     'nsfw': False,
    #     'postability': 5.64
    #     }

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