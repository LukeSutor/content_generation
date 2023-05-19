from dotenv import load_dotenv
import requests
import pandas
import os


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
                        'id': comment['name'],
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


def rank_comments(df, bounds, widen_factor=0):
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
        
    load_dotenv()
    default_bounds = tuple(map(int, bounds.split(",")))
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
    

def get_top_comment(post, bounds, headers=None):
    '''
    Given a post, get the top comment from it
    '''
    load_dotenv()
    bound_increase = int(os.getenv("BOUND_INCREASE"))

    # Get the first set of comments, and rank them, keeping track of all comments gathered
    comments, next_comments = accumulate_comments(post['id'], post['subreddit'], headers=headers)
    total_comments = pandas.DataFrame()
    total_comments = pandas.concat([total_comments, comments], ignore_index=True)
    comments = rank_comments(comments, bounds)

    # If no comments meet criteria, paginate through comments until there are no 
    # more results to get, keeping track of total comments
    while comments.shape[0] == 0:
        comments, new_next_comments = accumulate_comments(post['id'], post['subreddit'], 
                                                        headers=headers, next_comments=next_comments)
        total_comments = pandas.concat([total_comments, comments], ignore_index=True)
        if comments.empty:
            break
        comments = rank_comments(comments, bounds)
        next_comments = new_next_comments

    # If no posts can be found with the current bounds, 
    # gradually widen them until one is.
    current_bound_increase = bound_increase
    while comments.shape[0] == 0:
        running_total = total_comments.copy()
        comments = rank_comments(total_comments, bounds, widen_factor=current_bound_increase)
        current_bound_increase = current_bound_increase + bound_increase
        if current_bound_increase > 200:
            break

    # If a comment is found, set the top comment to it and fetch the author's avatar
    if comments.shape[0] != 0:
        top_comment = comments.iloc[0]
        top_comment['avatar'] = get_avatar(top_comment['author'], headers=headers)
    else:
        top_comment = False

    return top_comment