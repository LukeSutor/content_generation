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
        print(r)
    
    TOKEN = r.json()['access_token']

    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    return headers


def get_top_posts(subreddit, headers=None, final_id=None):
    '''
    Given a subreddit, fetch the top posts in the past 23 hours.
    If OAuth headers are passed, they will be used in the get request.
    '''
    load_dotenv()
    num_scrape = os.getenv("NUM_SCRAPE")

    # Based on whether a header and final ID is passed, call the proper endpoint
    if headers is not None:
        if final_id is not None:
            r = requests.get(f"https://oauth.reddit.com/r/{subreddit}/top.json?sort=top&t=23h&limit={num_scrape}&after={final_id}", headers=headers)
        else:
            r = requests.get(f"https://oauth.reddit.com/r/{subreddit}/top.json?sort=top&t=23h&limit={num_scrape}", headers=headers)
    else:
        if final_id is not None:
            r = requests.get(f"https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=23h&limit={num_scrape}&after={final_id}")
        else:
            r = requests.get(f"https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=23h&limit={num_scrape}")

    if(r.status_code == 200):
        return r.json()['data']['children']
    else:
        print(r)
        return False
    

def accumulate_posts(subreddits, headers=None, final_ids=None):
    '''
    Iterate through subreddits provided and get the specific number of posts to be
    saved to a pandas dataframe
    '''
    load_dotenv()
    num_scrape = os.getenv("NUM_SCRAPE")

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
                    'id': post['id'],
                    'upvotes': post['ups'],
                    'num_awards': post['total_awards_received'],
                    'num_comments': post['num_comments'],
                    'thumbnail': post['thumbnail'],
                    'awards': awards,
                    'nsfw': post['over_18'],
                    'subreddit': post['subreddit'],
                    'postability': 0
                }])
                df = pandas.concat([df, post_data], ignore_index=True)

    return df, new_final_ids


def rank_posts(df, widen_factor=0, ub_multiplier=1):
    '''
    Given a dataframe of posts, throw away unpostable ones, then calculate most postable one.

    widen_factor is used for expanding the upper bound to try to find a post
    ub_multiplier is used when trying to scrape a comment as well, shrinking the upper bound

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
    if df.shape[0] == 0:
        return df
    
    load_dotenv()
    default_bounds = tuple(map(int, os.getenv('WORDCOUNT_BOUNDS').split(",")))
    bounds = (max(0, default_bounds[0] - widen_factor), (default_bounds[1] + widen_factor))
    if ub_multiplier != 1:
        bounds[1] = int(ub_multiplier * bounds[1])

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


def get_top_comments(post_id, subreddit, headers=None):
    '''
    Given a post ID and subreddit, get the top comments from it.
    If OAuth headers are passed, they will be used in the get request.
    '''
    load_dotenv()
    num_scrape = os.getenv("NUM_SCRAPE")

    if headers is not None:
        r = requests.get(f"https://oauth.reddit.com/r/{subreddit}/comments/{post_id}.json?sort=top&limit={num_scrape}", headers=headers)
    else:
        r = requests.get(f"https://reddit.com/r/{subreddit}/comments/{post_id}.json?sort=best&limit={num_scrape}")

    if(r.status_code == 200):
        return r.json()[1]['data']['children']
    else:
        print(r)
        return False
    

def get_more_comments(parent_id, next_comments, headers=None):
    '''
    Given a parent comment ID and a list of following comment IDs, 
    get the comments.
    '''
    children_string = ",".join(next_comments)
    data = {
        'api_type': 'json',
        'link_id': parent_id,
        'sort': 'top',
        'children': children_string
    }

    if headers is not None:
        r = requests.post("https://oauth.reddit.com/api/morechildren", data=data, headers=headers)
    else:
        r = requests.post("https://reddit.com/api/morechildren", data=data)

    if(r.status_code == 200):
        return r.json()['json']['data']['things']
    else:
        print(r)
        return False


def accumulate_comments(post_id, subreddit, headers=None, next_comments=None):
    '''
    Given a post ID and subreddit, return the formatted comments
    and a list containing the IDs of the next comments to scrape.
    '''
    df = pandas.DataFrame()
    new_next_comments = []

    # Get comments using the post id and subreddit unless there are no more
    if next_comments == 'end':
        return df, 'end'
    elif next_comments is None:
        comments = get_top_comments(post_id, subreddit, headers=headers)
    else:
        comments = get_more_comments("t3_" + post_id, next_comments, headers=headers)

    if comments:
        # Loop through all supplied comments except the last one,
        # Which contains the IDs of more comments.
        for comment in comments:
            comment = comment['data']

            # Check to see if the element is actually a comment
            if "total_awards_received" in comment:
                # Gather award url(s)
                awards = []
                if comment['total_awards_received'] != 0:
                    for award in comment['all_awardings']:
                        awards.append(award['icon_url'])

                comment_data = pandas.DataFrame([{
                        'body': comment['body'],
                        'author': comment['author'],
                        'upvotes': comment['ups'],
                        'num_awards': comment['total_awards_received'],
                        'awards': awards,
                        'avatar': '',
                        'postability': 0
                    }])
                df = pandas.concat([df, comment_data], ignore_index=True)

        # Get ids of next comments
        if 'children' in comments[-1]:
            new_next_comments = comments[-1]['data']['children']
        else:
            new_next_comments = 'end'
            
    return df, new_next_comments


def rank_comments(df, widen_factor=0):
    '''
    Given a dataframe of comments, throw away unpostable ones, then calculate most postable one.

    widen_factor is used for expanding the upper bound to try to find a post

    Criteria for being postable:
        - Wordcount in range [50, 120]

    Posts are more postable if:
        - They have awards
        - They're longer in length (but still in the proper range)
        - They have more upvotes
        - Postability is calculated by:
            - (upvotes / 10) * word_count * (20**num_awards)
    '''
    if df.shape[0] == 0:
        return df
    
    # TODO: Change the bounds to work if the user wants a comment or not
    
    load_dotenv()
    default_bounds = tuple(map(int, os.getenv('WORDCOUNT_BOUNDS').split(",")))
    # Automatically multiply the upper bound by 0.5 because you're fetching a comment
    bounds = (default_bounds[0], int(0.5 * (default_bounds[1] + widen_factor)))

    drop_indices = []
    # Iterate through posts and check all conditions.
    # Then calculate postability if all conditions met.
    for index in range(df.shape[0]):
        wordcount = len(df.iloc[index]['body'].split(" "))
        if wordcount not in range(*bounds):
            drop_indices.append(index)
        else:
            postability = (df.iloc[index]['upvotes'] / 10) * wordcount * (20**df.iloc[index]['num_awards'])
            df.at[index, 'postability'] = postability

    # Drop unpostables and sort the rest by postability
    df.drop(drop_indices, inplace=True)
    df = df.sort_values(by='postability', ascending=False)

    return df


def get_avatar(username, headers=None):
    '''
    Given a Reddit username, get a link to their avatar picture.
    '''
    if headers is not None:
        r = requests.get(f"https://oauth.reddit.com/user/{username}/about.json", headers=headers)
    else:
        r = requests.get(f"https://reddit.com/user/{username}/about.json")

    if r.status_code == 200:
        return r.json()['data']['subreddit']['icon_img']
    else:
        print(r)
        return ''


def get_top_post(subreddits, comment=False):
    '''
    Get the most postable reddit post (and comment if applicable) from the subreddit(s) given
    '''
    load_dotenv()
    bound_increase = int(os.getenv("BOUND_INCREASE"))
    
    headers = get_oauth_headers()

    # Get the first set of posts, and rank them, keeping track of all posts gathered
    posts, final_ids = accumulate_posts(subreddits, headers=headers)
    total_posts = pandas.DataFrame()
    total_posts = pandas.concat([total_posts, posts], ignore_index=True)
    posts = rank_posts(posts)

    # If no posts meet criteria, paginate through posts until there are no 
    # more results to get, keeping track of total posts
    while posts.shape[0] == 0:
        posts, new_final_ids = accumulate_posts(subreddits, headers=headers, final_ids=final_ids)
        total_posts = pandas.concat([total_posts, posts], ignore_index=True)
        if posts.empty:
            break
        posts = rank_posts(posts)
        final_ids = new_final_ids

    # If no posts can be found with the current bounds, 
    # gradually widen them until one is.
    current_bound_increase = bound_increase
    while posts.shape[0] == 0:
        running_total = total_posts.copy()
        posts = rank_posts(running_total, current_bound_increase)
        current_bound_increase = current_bound_increase + bound_increase
        if current_bound_increase > 300:
            break

    # If no post is found STILL, throw an exception and terminate
    if posts.shape[0] == 0:
        raise Exception("No posts could be found")
    
    top_post = posts.iloc[0]
    
    # If comment is True, do a process similar to before but for comments
    top_comment = False
    if comment:
        # Get the first set of comments, and rank them, keeping track of all comments gathered
        comments, next_comments = accumulate_comments(top_post['id'], top_post['subreddit'], headers=headers)
        total_comments = pandas.DataFrame()
        total_comments = pandas.concat([total_comments, comments], ignore_index=True)
        comments = rank_comments(comments)

        # If no comments meet criteria, paginate through comments until there are no 
        # more results to get, keeping track of total comments
        while comments.shape[0] == 0:
            comments, new_next_comments = accumulate_comments(top_post['id'], top_post['subreddit'], 
                                                            headers=headers, next_comments=next_comments)
            total_comments = pandas.concat([total_comments, comments], ignore_index=True)
            if comments.empty:
                break
            comments = rank_comments(comments)
            next_comments = new_next_comments

        # If no posts can be found with the current bounds, 
        # gradually widen them until one is.
        current_bound_increase = bound_increase
        while comments.shape[0] == 0:
            running_total = total_comments.copy()
            comments = rank_comments(total_comments, current_bound_increase)
            current_bound_increase = current_bound_increase + bound_increase
            if bound_increase > 500:
                break

        # If a comment is found, set the top comment to it and fetch the author's avatar
        if comments.shape[0] != 0:
            top_comment = comments.iloc[0]
            top_comment['avatar'] = get_avatar(top_comment['author'], headers=headers)

    return top_post, top_comment


if __name__ == "__main__":    
    subreddits = [
                # "TalesFromRetail",
                # "AmItheAsshole",
                # "Showerthoughts",
                # "dadjokes",
                "AskReddit",
                # "tifu",
                # "talesfromtechsupport",
                # "humor",
                # "Cleanjokes",
                # "Jokes",
                # "Punny",
                # "Lightbulb",
                # "StoriesAboutKevin",
                # "TodayILearned",
                ]

    # top_post, top_comment = get_top_post(subreddits, True)

    # if type(top_comment) != bool:
    #     print(top_post['title'], top_post['body'], top_comment['body'], sep="\n\n")
    # else:
    #     print(top_post['title'], top_post['body'], top_post['num_comments'], sep="\n\n")

    get_avatar('lukesutor', headers=get_oauth_headers())