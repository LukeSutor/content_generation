import requests
import pandas
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
                post_data = pandas.DataFrame([{
                    'title': post['title'],
                    'body': post['selftext'],
                    'author': post['author'],
                    'upvotes': post['ups'],
                    'upvote_ratio': post['upvote_ratio'],
                    'num_awards': post['total_awards_received'],
                    'num_comments': post['num_comments'],
                    'thumbnail': post['thumbnail'],
                    'postability': 0
                }])
                df = pandas.concat([df, post_data], ignore_index=True)

    return df


def rank_posts(df):
    '''
    Given a dataframe of posts, rank the posts and reorder them by measure of post-ability

    Post-abiility is determined by the following:
        (((upvotes * upvote_ratio) + (num_comments * 2)) / wordcount) * (num_awards + 1)
    There is also a max word count of 200 words allowed.
    '''

    drop_indices = []

    for index in range(df.shape[0]):
        # First, throw away posts with images or bad word count by saving the index to drop it later
        wordcount = len(df.iloc[index]['body'].split(" ")) + len(df.iloc[index]['title'].split(" "))
        if wordcount not in range(20, 100) or df.iloc[index]['thumbnail'] != "":
            drop_indices.append(index)
            pass

        # Calculate postability
        upvote_num = df.iloc[index]['upvotes'] * df.iloc[index]['upvote_ratio']
        comments_num = df.iloc[index]['num_comments'] * 2
        ratio = (upvote_num + comments_num) / wordcount
        postability = ratio * (df.iloc[index]['num_awards'] + 1)
        
        df.at[index, 'postability'] = postability

    # Drop posts
    df.drop(drop_indices, inplace=True)

    df = df.sort_values(by='postability', ascending=False)

    return df


def get_top_post(subreddits, n):
    posts = accumulate_posts(subreddits, n)

    posts = rank_posts(posts)

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
