import requests

def get_top_posts(subreddit, n):
    '''
    Given a subreddit, fetch the top n posts in the past 24 hours.
    '''
    r = requests.get(f"https://www.reddit.com/r/{subreddit}/top.json?sort=top&t=day&limit={n}")

    if(r.status_code == 200):
        return r.json()
    else:
        return False

if __name__ == "__main__":
    subreddits = ["TalesFromRetail",
                "AmItheAsshole",
                "Showerthoughts",
                "dadjokes"]
    
    posts = get_top_posts(subreddits[1], 5)

    if posts:
        print(len(posts['data']['children']))