# Social Media Content Generation
This project involves scraping content from reddit and turning it into TikTok / Instagram Reels type posts.  

## The Pipeline:
- First, relevant subreddits are scraped using the Reddit OAuth API. The data is then saved to a dataframe including the fields:
    - Title
    - Body
    - Author
    - Upvotes
    - Number of Awards
    - Number of Comments
    - Thumbnail
    - Awards
    - NSFW
    - Postability
- Next, these posts are passed through a ranking algorithm to find the most content-worthy one. The algorithm is as follows:
    - Posts must be between 40 and 120 words in length including the title, include no images, and not be NSFW.
    - If the posts meet the above criteria, a "post-ability" value is calculated based on:  
    `(upvotes / 10) * word_count * (20**num_awards)`  
    This ensures the content is popular and gives a significant favorance to posts with awards.
- The post with the highest post-ability rating is then passed on to the image creation step in which the library html2image is used to create a png image of what the reddit post would look like on the web.
- AWS Polly is then used to create a voiceover of the title and description of the post
- Finally, the post image, voiceover, and a random snippet of a gaming video are stitched together using MoviePy to create the post.