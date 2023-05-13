from dotenv import load_dotenv
import requests
import pandas
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


def get_top_posts(subreddit, headers=None, final_id=None):
    '''
    Given a subreddit, fetch the top n posts in the past 24 hours.
    If OAuth headers are passed, they will be used in the get request.
    '''
    load_dotenv()
    
    num_scrape = os.getenv("NUM_SCRAPE")

    # Based on whether a header and final ID is passed, call the proper endpoint
    if headers is not None:
        if final_id is not None:
            r = requests.get(f"https://oauth.reddit.com/r/{subreddit}/top.json?sort=top&t=23h&limit={500}&after={final_id}", headers=headers)
        else:
            r = requests.get(f"https://oauth.reddit.com/r/{subreddit}/top.json?sort=top&t=23h&limit={500}", headers=headers)
    else:
        if final_id is not None:
            r = requests.get(f"https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=23h&limit={num_scrape}&after={final_id}")
        else:
            r = requests.get(f"https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=23h&limit={num_scrape}")

    if(r.status_code == 200):
        return r.json()['data']['children']
    else:
        print(r.json())
        return False
    

def accumulate_posts(subreddits, final_ids=None):
    '''
    Iterate through subreddits provided and get the specific number of posts to be
    saved to a pandas dataframe
    '''
    load_dotenv()
    
    num_scrape = os.getenv("NUM_SCRAPE")

    headers = get_oauth_headers()

    df = pandas.DataFrame()
    
    if final_ids is None:
        final_ids = [None] * len(subreddits)

    new_final_ids = [None] * len(subreddits)

    for i, subreddit in enumerate(subreddits):
        # Scrape more posts until the end is reached
        if final_ids[i] != 'end':
            subreddit_posts = get_top_posts(subreddit, headers, final_ids[i])
        else:
            subreddit_posts = []
        
        # Only append a final ID if it's possible to get more posts
        if len(subreddit_posts) == int(num_scrape):
            new_final_ids[i] = subreddit_posts[-1]['data']['name']
        else:
            new_final_ids[i] = 'end'

        if subreddit_posts:
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

    return df, new_final_ids


def rank_posts(df, widen_factor=0):
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
    load_dotenv()

    default_bounds = tuple(map(int, os.getenv('WORDCOUNT_BOUNDS').split(",")))
    bounds = (max(0, default_bounds[0] - widen_factor), (default_bounds[1] + widen_factor))

    drop_indices = []
    # Iterate through posts and check all conditions.
    # Then calculate postability if all conditions met.
    for index in range(df.shape[0]):
        wordcount = len(df.iloc[index]['body'].split(" ")) + len(df.iloc[index]['title'].split(" "))
        if wordcount not in range(*bounds) or df.iloc[index]['thumbnail'] != "" or df.iloc[index]['nsfw']:
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
    load_dotenv()
    bound_increase = int(os.getenv("BOUND_INCREASE"))

    # Try to get num_posts posts, and use pagination to get more results if necessary
    posts, final_ids = accumulate_posts(subreddits)
    total_posts = pandas.DataFrame()
    total_posts = pandas.concat([total_posts, posts], ignore_index=True)
    posts = rank_posts(posts)

    # TODO: add proper pagination for post selection https://www.reddit.com/dev/api/#GET_{sort}

    # Keep on paginating until there are no more results to get, keeping track of total posts
    while posts.shape[0] == 0:
        posts, new_final_ids = accumulate_posts(subreddits, final_ids)
        total_posts = pandas.concat([total_posts, posts], ignore_index=True)
        if posts.empty:
            break
        posts = rank_posts(posts)
        final_ids = new_final_ids

    # If no posts can be found with the current bounds, 
    # gradually widen them until one is.
    while posts.shape[0] == 0:
        posts = rank_posts(total_posts, bound_increase)
        bound_increase += bound_increase
        if bound_increase > 500:
            break

    # If no post is found STILL, throw an exception and terminate
    if posts.shape[0] == 0:
        raise Exception("No posts could be found")

    return posts.iloc[0]


if __name__ == "__main__":    
    subreddits = [
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
                ]

    post = get_top_post(subreddits)
    
    print("Title:", post['title'], "\nBody:", post['body'])