from post_collector import get_top_post
from image_creator import create_image
from voiceover_creator import create_voiceover


if __name__ == "__main__":
    FILENAME = 'top_post.png'
    NUM_POSTS = 25
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
    
    # post = get_top_post(SUBREDDITS, NUM_POSTS)

    post = {
        'title': 'Why did the chicken cross the road?',
        'body': 'To get to the other side.',
        'author': 'PixelatedNPC',
        'upvotes': 350,
        'upvote_ratio': 0.95,
        'num_awards': 1,
        'num_comments': 525,
        'thumbnail': '',
        'postability': 5.423
    }

    # create_image(post, FILENAME)

    create_voiceover(post)
