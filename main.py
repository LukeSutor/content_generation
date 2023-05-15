from utilities.post_collector import get_top_post
from utilities.image_creator import create_image
from utilities.voiceover_creator import create_voiceover
from utilities.video_creator import create_video
from dotenv import load_dotenv
import datetime
import argparse
import os


def cleanup(post_name, comment=False):
    '''
    Given a post name, clean up the unneseccary png and mp3 files.
    '''
    save_dir = os.getenv('SAVE_PATH')

    os.remove(os.path.join(save_dir, post_name + ".png"))
    os.remove(os.path.join(save_dir, post_name + ".mp3"))
    
    # Do the same for the comment if it exists
    if comment:
        os.remove(os.path.join(save_dir, post_name + "_comment" + ".png"))
        os.remove(os.path.join(save_dir, post_name + "_comment" + ".mp3"))


def create_post():
    '''
    Given a background folder containing background videos and subreddit(s)
    to scrape, create a reel.

    post_name is optional, and if it isn't given the post will be named the current datetime
    '''
    parser = argparse.ArgumentParser(prog='Content Generation Bot', 
                                     description='Generate TikTok style content from Reddit posts')
    parser.add_argument('-s', '--subreddits', type=str, nargs='+',
                        help='A list of subreddits to scrape from', required=True)
    parser.add_argument('-n', '--name', type=str, default=None,
                        help='A name for the post', required=False)
    parser.add_argument('-c', '--comment', type=bool, nargs=1, default=False,
                        help='Boolean wether or not to scrape a comment with the Reddit post', required=False)
    
    args = parser.parse_args()
    subreddits = args.subreddits
    post_name = args.name
    fetch_comment = args.comment

    load_dotenv()
    save_path = os.getenv('SAVE_PATH')

    if post_name is None:
        post_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    post, comment = get_top_post(subreddits, fetch_comment)

    # If you were trying to fetch a comment but couldn't, set fetch_comment to false
    if not fetch_comment or (fetch_comment and type(comment) == bool and not comment):
        fetch_comment = False
        comment = None

    create_image(post, post_name, comment=comment)

    create_voiceover(post, post_name, comment=comment)

    create_video(post_name, comment=fetch_comment)

    cleanup(post_name, comment=fetch_comment)


if __name__ == "__main__":
    # example_post = {
    #     'title': 'Example Post',
    #     'body': 'This post was created using the content generation pipeline.',
    #     'author': 'lukesutor',
    #     'upvotes': 2100,
    #     'num_awards': 0,
    #     'num_comments': 323,
    #     'thumbnail': '',
    #     'awards': [],
    #     'nsfw': False,
    #     'postability': 5.64
    #     }

    # SUBREDDITS = (
    #             "TalesFromRetail",
    #             "AmItheAsshole",
    #             "Showerthoughts",
    #             "dadjokes",
    #             # "AskReddit",
    #             "tifu",
    #             "talesfromtechsupport",
    #             "humor",
    #             "Cleanjokes",
    #             "Jokes",
    #             "Punny",
    #             "Lightbulb",
    #             "StoriesAboutKevin",
    #             "TodayILearned",
    #             )
    
    '''
    Command to scrape all subreddits:
python main.py -s TalesFromRetail AmItheAsshole Showerthoughts dadjokes tifu talesfromtechsupport humor Cleanjokes Jokes Punny Lightbulb StoriesAboutKevin TodayILearned
    '''
    
    create_post()