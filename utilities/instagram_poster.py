import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


def login(driver):
    '''
    Given the selenium driver, log in
    to the user account
    '''
    load_dotenv()
    username = os.getenv("INSTAGRAM_USERNAME")
    password = os.getenv("INSTAGRAM_PASSWORD")

    driver.get("https://www.instagram.com/")

    # Wait for page load
    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
    except Exception as e:
        print(e)
        raise Exception("Username field couldn't be found.")
    
    # log in
    password_field = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.CLASS_NAME, "_acap")

    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

    return driver


def create_caption(post):
    '''
    Create a post caption with hashtags and the username of the Reddit poster
    '''
    load_dotenv()
    hashtags = os.getenv("INSTAGRAM_HASHTAGS")
    username = os.getenv("INSTAGRAM_USERNAME")

    title = post['title']
    author = post['author']

    caption = title + "\nBy u/" + author + "\nFollow @" + username + " for more daily content🔥" + "\n\n\nTags:\n" + hashtags

    return caption


def upload_and_post(driver, filename, caption):
    '''
    Navigate to where reels are posted
    '''
    load_dotenv()
    save_path = os.getenv("SAVE_PATH")

    # Wait for sidebar
    try:
        _ = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "x19c4wfv"))
        )
    except Exception as e:
        print(e)
        raise Exception("Sidebar didn't load")
    
    sidebar_buttons = driver.find_elements(By.CLASS_NAME, "x19c4wfv")

    sidebar_buttons[7].click()

    # Wait for upload button
    try:
        _ = WebDriverWait(driver, 10).until(
            EC.title_contains("Create new post")
        )
    except Exception as e:
        print(e)
        raise Exception("Upload button didn't load")
    
    # Send post to upload input
    post_path = os.path.join(os.getcwd(), save_path, filename + ".mp4")
    upload_link = driver.find_element(By.CLASS_NAME, "_ac69")
    upload_link.send_keys(post_path)

    # Wait for okay button
    try:
        okay_button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_acaq"))
        )
    except Exception as e:
        print(e)
        raise Exception("Post didn't upload")
    okay_button.click()

    # Set aspect ratio to 9*16
    aspect_button = driver.find_elements(By.CLASS_NAME, "xwib8y2")[2]
    aspect_button.click()
    nine_sixteen = driver.find_elements(By.CLASS_NAME, "_acao")[2]
    nine_sixteen.click()
    next_button = driver.find_elements(By.CLASS_NAME, "x1yc6y37")[1]
    next_button.click()

    # Wait for trim section
    try:
        _ = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "_aabn"))
        )
    except Exception as e:
        print(e)
        raise Exception("Couldn't navigate to the trim post screen")
    next_button = driver.find_elements(By.CLASS_NAME, "x1yc6y37")[1]
    next_button.click()

    # Wait for caption section and set it
    try:
        caption_section = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "notranslate"))
        )
    except Exception as e:
        print(e)
        raise Exception("Couldn't navigate to the add caption section")
    caption_section.click()
    
    actions = ActionChains(driver)
    actions.send_keys(caption)
    actions.perform()

    # Share it
    share_button = driver.find_elements(By.CLASS_NAME, "x1yc6y37")[1]
    share_button.click()

    # Wait until the post is shared, or 2 minutes pass, to close
    posted = False
    shared_text = ""
    for _ in range(60):
        try:
            shared_text = driver.find_element(By.CLASS_NAME, "xw06pyt").get_attribute('innerText')
            print(shared_text)
        except:
            time.sleep(2)
            pass
        if shared_text == "Your reel has been shared.":
            posted = True
            break
        elif shared_text == "Your post could not be shared. Please try again.":
            try_again = driver.find_element(By.CLASS_NAME, "x1yc6y37")
            try_again.click()
        else:
            time.sleep(2)

    if not posted:
        raise Exception("Post could not be posted.")



def post_reel(filename, post):
    '''
    Given the reel's filename, post it.
    '''
    driver = webdriver.Chrome()
    driver = login(driver)
    caption = create_caption(post)
    driver = upload_and_post(driver, filename, caption)



if __name__ == "__main__":
    example_post = {
        'title': 'Example Post',
        'body': 'This post was created using the content generation pipeline.',
        'author': 'lukesutor',
        'upvotes': 2100,
        'num_awards': 0,
        'num_comments': 323,
        'thumbnail': '',
        'awards': [],
        'nsfw': False,
        'postability': 5.64
        }
    post_reel("example_post_1", example_post)
    
    # print(create_caption(example_post))
