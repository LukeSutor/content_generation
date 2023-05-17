import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


def upload_and_post(driver):
    '''
    Navigate to where reels are posted
    '''

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
    
    upload_button = driver.find_elements(By.CLASS_NAME, "_acap")[1]

    upload_button.click()

    time.sleep(4)



def post_reel(filename):
    '''
    Given the reel's filename, post it.
    '''
    load_dotenv()
    save_path = os.getenv("SAVE_PATH")

    driver = webdriver.Chrome()
    driver = login(driver)
    driver = upload_and_post(driver)



if __name__ == "__main__":
    post_reel("test")
