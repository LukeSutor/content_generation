from post_collector import get_top_post
from image_creator import create_image
from voiceover_creator import create_voiceover
from video_creator import create_video
import os


def cleanup(post_name):
    '''
    Given a post name, clean up the unneseccary png and mp3 files.
    '''
    os.remove(post_name + ".png")
    os.remove(post_name + ".mp3")


def create_post(post_name, num_scrape, background_folder, subreddits):
    '''
    Given a post name, the number of posts to scrape, a background folder containing
    background videos, and a list of subreddits, create a reel.
    '''
    post = get_top_post(subreddits, num_scrape)

    create_image(post, post_name)

    create_voiceover(post, post_name)

    create_video(post_name, background_folder)

    cleanup(post_name)

    print("Done! post created and saved under ", post_name, ".mp4", sep="")



if __name__ == "__main__":
    POST_NAME = 'real_post'
    NUM_POSTS = 25
    BACKROUND_VIDEO_FOLDER = './gaming_videos'
    SUBREDDITS = ("TalesFromRetail",
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
                "TodayILearned",)
    
    create_post(POST_NAME, NUM_POSTS, BACKROUND_VIDEO_FOLDER, SUBREDDITS)