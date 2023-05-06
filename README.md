# Social Media Content Generation
This project involves scraping content from reddit posts and turning it into social media posts.  

## The Pipeline:
- First, relevant subreddits are scraped using the Reddit OAuth API. The data is then saved to a dataframe including the fields:
    - Title
    - Body
    - Author
    - Upvotes
    - Upvote Ratio
    - Number of Awards
    - Number of Comments
    - Thumbnail
- Next, these posts are passed through a ranking algorithm to find the most content-worthy one. The algorithm is as follows:
    - Posts must be between 20 and 99 words in length including the title, (brevity is important for reels content) and include no images.
    - If the posts meet the above criteria, a "post-ability" value is calculated based on:  
    `(((upvotes * upvote_ratio) + (num_comments * 2)) / wordcount) * (num_awards + 1)`  
    This ensures the content is popular and gives a significant favorance to posts with awards.
- The post with the highest post-ability rating is then passed on to the image creation step in which the library html2image is used to create a png image of what the reddit post would look like on the web.