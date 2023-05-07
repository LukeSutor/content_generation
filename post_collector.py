import requests
import pandas
import math
from dotenv import load_dotenv
import os


def get_oauth_headers():
    '''
    Using the environment variables saved in .env, get an OAuth token and return a header
    '''
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    secret_token = os.getenv("SECRET_TOKEN")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("PASSWORD")

    auth = requests.auth.HTTPBasicAuth(client_id, secret_token)

    data = {'grant_type': 'password',
        'username': username,
        'password': password}
    
    headers = {'User-Agent': 'Content_Scraper/0.1'}

    r = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)
    
    if r.status_code != 200:
        print(r.json())
    
    TOKEN = r.json()['access_token']

    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    return headers


def get_top_posts(subreddit, n, headers=None):
    '''
    Given a subreddit, fetch the top n posts in the past 24 hours.
    If OAuth headers are passed, they will be used in the get request.
    '''
    if headers is not None:
        r = requests.get(f"https://oauth.reddit.com/r/{subreddit}/top.json?sort=top&t=day&limit={n}", headers=headers)
    else:
        r = requests.get(f"https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=day&limit={n}")

    if(r.status_code == 200):
        return r.json()['data']['children']
    else:
        print(r.json())
        return False
    

def accumulate_posts(subreddits, n):
    '''
    Iterate through subreddits provided and get the specific number of posts to be
    saved to a pandas dataframe
    '''
    headers = get_oauth_headers()

    df = pandas.DataFrame()

    for subreddit in subreddits:
        subreddit_posts = get_top_posts(subreddit, n, headers)

        if not subreddit_posts:
            print("Error fetching posts from", subreddit, "subreddit.")
        else:
            for post in subreddit_posts:
                post = post['data']
                # Gather award url(s)
                awards = []
                if post['total_awards_received'] != 0:
                    for award in post['all_awardings']:
                        awards.append(award['icon_url'])

                post_data = pandas.DataFrame([{
                    'title': post['title'],
                    'body': post['selftext'],
                    'author': post['author'],
                    'upvotes': post['ups'],
                    'num_awards': post['total_awards_received'],
                    'num_comments': post['num_comments'],
                    'thumbnail': post['thumbnail'],
                    'awards': awards,
                    'nsfw': post['over_18'],
                    'postability': 0
                }])
                df = pandas.concat([df, post_data], ignore_index=True)

    return df


def rank_posts(df):
    '''
    Given a dataframe of posts, throw away unpostable ones, then calculate most postable one.

    Criteria for being postable:
        - Wordcount in range [50, 120]
        - Not NSFW
        - No images

    Posts are more postable if:
        - They have awards
        - They're longer in length (but still in the proper range)
        - They have more upvotes
        - Postability is calculated by:
            - (upvotes / 10) * word_count * (20**num_awards)
    '''

    drop_indices = []

    # Iterate through posts and check all conditions.
    # Then calculate postability if all conditions met.
    for index in range(df.shape[0]):
        wordcount = len(df.iloc[index]['body'].split(" ")) + len(df.iloc[index]['title'].split(" "))
        if wordcount not in range(40, 121) or df.iloc[index]['thumbnail'] != "" or df.iloc[index]['nsfw']:
            drop_indices.append(index)
        else:
            postability = (df.iloc[index]['upvotes'] / 10) * wordcount * (20**df.iloc[index]['num_awards'])
            df.at[index, 'postability'] = postability

    # Drop unpostables and sort the rest by postability
    df.drop(drop_indices, inplace=True)
    df = df.sort_values(by='postability', ascending=False)

    return df


def get_top_post(subreddits):
    '''
    Get the most postable reddit post from the subreddit(s) given
    '''
    posts = accumulate_posts(subreddits, 50)
    posts = rank_posts(posts)

    n = 100
    while posts.shape[0] == 0:
        posts = accumulate_posts(subreddits, n)
        posts = rank_posts(posts)
        n+=50

    top_post = posts.iloc[0]
    return top_post


if __name__ == "__main__":    
    subreddits = ["TalesFromRetail",
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
                "TodayILearned",]
    
    posts = accumulate_posts(subreddits, 25)

    posts = rank_posts(posts)
    
    for i in range(10):
        print("Post {} title:".format(i), posts.iloc[i]['title'], "\n")
        print("Post {} body:".format(i), posts.iloc[i]['body'], "\n\n")