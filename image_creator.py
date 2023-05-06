from html2image import Html2Image
import random
import math
import numpy as np
from PIL import Image


def create_html_image(post, filename):
    '''
    Takes in a dataframe of a post and creates an html document of it.
    Then uses html2image to take a screenshot of said html.
    '''

    with open("RedditPost.html", "r") as f:
        document = f.read()

    # Format the body
    body = post['body']
    body = body.replace('\n', '<br />')

    # Format the upvotes
    upvotes = int(post['upvotes'])
    if upvotes >= 1000:
        upvotes = str(upvotes // 100 / 10) + "k"
    else:
        upvotes = str(upvotes)

    # Set the text for all the elements
    document = document.replace("_/title/_", post['title'])
    document = document.replace("_/body/_", body)
    document = document.replace("_/username/_", post['author'])
    document = document.replace("_/upvotes/_", upvotes)
    document = document.replace("_/num_comments/_", str(post['num_comments']))
    # Make the time a random number between 2 and 23 hours
    document = document.replace("_/time/_", str(math.ceil(random.random() * 21 + 1)))


    # Take HTML screenshot
    hti = Html2Image()

    hti.screenshot(html_str=document, save_as=(filename + ".png"))


def row_same(row):
    '''
    Given a row of an image, return True if all the elements are the same.
    '''
    for i in range(1, len(row)):
        if row[0] != row[i] and not row[i]:
            return False
        
    return True


def col_same(array, index):
    '''
    Given an array and a column index, return True if all the elements are the same.
    '''
    for i in range(len(array)):
        if array[i][0] != array[i][index]:
            return False
        
    return True


def clean_image(filename):
    '''
    Given a filename, remove the black background and unnecessary pixels from the image.
    '''

    image = Image.open(filename + ".png")

    image = np.asarray(image.convert("RGBA"))

    # Get ids of black pixels and set to transparent
    idx = (image[...,:3] == np.array((0,0,0))).all(axis=-1)
    image[idx,3] = 0

    # Delete all fully-transparent rows
    transparent_rows = []
    idx = np.asarray(idx)
    for i, row in enumerate(idx):
        if row_same(row):
            transparent_rows.append(i)

    idx = np.delete(idx, transparent_rows, 0)
    image = np.delete(image, transparent_rows, 0)

    # # Do the same for columns
    transparent_rows.clear()
    for i in range(len(idx[0])):
        if col_same(idx, i):
            transparent_rows.append(i)

    image = np.delete(image, transparent_rows, 1)

    # Save image
    image = Image.fromarray(image)

    image = image.save(filename + ".png")


def create_image(post, filename):
    '''
    Helper function to create and clean a post image.
    '''
    create_html_image(post, filename)
    clean_image(filename)


if __name__ == "__main__":
    pass
