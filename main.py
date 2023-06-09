from utilities.post_collector import get_top_post
from utilities.comment_collector import get_top_comment
from utilities.image_creator import create_image
from utilities.voiceover_creator import create_voiceover
from utilities.video_creator import create_video
from utilities.instagram_poster import post_reel
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
    
    # Do the same for the comment files if they were created
    if comment:
        os.remove(os.path.join(save_dir, post_name + "_comment" + ".png"))
        os.remove(os.path.join(save_dir, post_name + "_comment" + ".mp3"))
        os.remove(os.path.join(save_dir, "silence.mp3"))


def create_post():
    '''
    Given a background folder containing background videos and subreddit(s)
    to scrape, create a reel.

    post_name is optional, and if it isn't given the post will be named the current datetime
    '''
    parser = argparse.ArgumentParser(prog='Content Generation Bot', 
                                     description='Generate TikTok style content from Reddit posts')
    parser.add_argument('-s', '--subreddits', type=str, nargs='+',
                        help='A list of subreddits to scrape from.', required=True)
    parser.add_argument('-n', '--name', type=str, default=None,
                        help='A name for the post.', required=False)
    parser.add_argument('-b', '--bounds', type=str, default="8,121",
                        help='Wordcount bounds formatted lb,ub.', required=False)
    parser.add_argument('-c', '--comment', action='store_true', required=False,
                        help='Whether or not to scrape a comment along with the post.')
    parser.add_argument('-u', '--upload', action='store_true', required=False,
                        help='Whether or not to upload the post to Instagram.')
    parser.add_argument('-a', '--anonymize', action='store_true', required=False,
                        help='Whether or not to anonymize the user(s) scraped.')
    
    args = parser.parse_args()
    subreddits = args.subreddits
    post_name = args.name
    wordcount_bounds = args.bounds
    fetch_comment = args.comment
    upload = args.upload
    anonymize = args.anonymize

    load_dotenv()
    save_dir = os.getenv('SAVE_PATH')

    # Create a post name if none was given
    if post_name is None:
        post_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    post, headers = get_top_post(subreddits, wordcount_bounds)
    comment = get_top_comment(post, wordcount_bounds, headers=headers)

    # If you were trying to fetch a comment but couldn't, set fetch_comment to false
    if not fetch_comment or (fetch_comment and type(comment) == bool and not comment):
        fetch_comment = False
        comment = None

    # If anonymize is passed, anonymize the user(s)
    if anonymize:
        post['author'] = "AnonymousUser"
        if comment is not None:
            comment['author'] = "AnonymousUser"
            comment['avatar'] = "https://www.redditstatic.com/avatars/avatar_default_02_A5A4A4.png"

    create_image(post, post_name, comment=comment)

    create_voiceover(post, post_name, comment=comment)

    create_video(post_name, comment=fetch_comment)

    cleanup(post_name, comment=fetch_comment)

    if upload:
        post_reel(post_name, post)

    print("Done.")


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
    #             "AskReddit",
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