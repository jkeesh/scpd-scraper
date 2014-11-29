"""

Scrapes the SCPD site and downloads lecture videos for the given course.

Note that since the SCPD site update, you must be enrolled in the course to
successfully download the videos.

Usage:
    python scrape.py [yourUserName] [optional flags] cs/103 cs/106x

"""

import re
import os
import sys
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

DOWNLOAD_URL_PREFIX = "https://mvideox.stanford.edu/Graduate#/CourseDetail"

# YOU MUST MODIFY THESE AS APPROPRIATE
# TODO get the current values programmatically
QUARTER = "Autumn"
YEAR = "2014"

# Flags
ALL_FLAG = "--all"
HELP_FLAG = "--help"
NEW_FIRST_FLAG = "--priority=new"
OUTPUT_PATH_FLAG = "--outputPath="


def already_downloaded(file_name, course_name, output_path):
    """Check directories for the video to see if it's downloaded already.

    Parameters
    ----------
    file_name: str
        file name of the video (not full path, just name like "thevideo.mp4")
    course_name: str
        name of the course
    output_path: str
        path to the video download location

    Return whether the video with the given file name was downloaded already.

    """
    directories = [
        output_path + file_name,
        course_name + "/" + file_name,
        output_path + "watched/" + file_name
    ]
    return any(os.path.exists(directory) for directory in directories)

def download(video_url, destination_file_name, course_name, download_settings):
    """Download the video with the given url.

    Parameters
    ----------
    video_url: str
        url of the video to download
    destination_file_name: str
        name of the file to download the video to locally (e.g. "thevideo.mp4")
    course_name: str
        name of the course
    download_settings: dict
        dictionary of settings for the download

    """
    if already_downloaded(destination_file_name, course_name, download_settings["outputPath"]):
        print "Already downloaded %s" % destination_file_name
        return

    print "Starting download for %s" % destination_file_name

    # If the user didn't give an output path, output to coursename folder.
    if download_settings["outputPath"] == "":
        course_path = course_name.replace(" ", "\ ") # spaces break command line navigation
        assert_directory_exists(course_name)
        destination_file_name = course_path + "/" + destination_file_name
    else:
        destination_file_name = download_settings["outputPath"] + destination_file_name

    os.system("wget -O %s %s" % (destination_file_name, video_url))

    print "Finished", destination_file_name

def assert_directory_exists(dir):
    """Check if a directory exists. Make one if not.

    Parameters
    ----------
    dir: str
        directory name to check

    """
    if not os.path.exists(dir):
        os.makedirs(dir)

def contains_form_by_name(browser, formName):
    """Check if the browser's page has a form with the given name.

    Parameters
    ----------
    browser: Browser
        the browser whose page to check
    formName: str
        name of the form to check

    """
    return formName in [form.name for form in browser.forms()]

def download_course_lectures(driver, course_name, download_settings):
    """Download all the lectures for the course with the given url.

    Parameters
    ----------
    driver: webdriver
        the driver to open the web page with
    course_name: str
        name of the course
    download_settings: dict
        dictionary of settings for the download

    """
    course_url = get_course_url(course_name)

    driver.get(course_url)

    # Build up a list of lectures
    print '\n=== Starting "' + course_name + '" ==='
    print "Loading video links."

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "btn-link"))
    )
    anchor_tags = driver.find_elements_by_class_name("btn-link")

    links = []
    video_ids = [] # Used solely to avoid duplicates
    for i, anchor_tag in enumerate(anchor_tags):
        href = anchor_tag.get_attribute("href")

        # We always want the high quality version of the video.
        # This seemed to be the easiest way to figure out if it was high or low
        # quality as looking at the button's text didn't work for some reason.
        if 'Low' in anchor_tag.get_attribute('ng-click'): continue
        
        # Get the id of this video.
        video_id = re.search("^http://html5b.stanford.edu/videos/courses/cs107/(\d+)-", href).group(1)
        video_id = int(video_id)

        # If we haven't already seen this video, add it to the list.
        if video_id not in video_ids:
            links.append(href)
            video_ids.append(video_id)

    # This relies on the fact that the videos are listed most recent first on the webpage.
    videos = [(href, "lecture_%d.mp4" % (len(links) - i)) for i, href in enumerate(links)]

    if not download_settings["newestFirst"]:
        videos.reverse()

    print "Downloading %d video streams." % len(videos)
    for video in videos:
        download(video[0], video[1], course_name, download_settings)
    print "Done!"

def login(username):
    """Log the user into the Stanford webauth system.

    Parameters
    ----------
    username: str
        username of the user to log in

    Return webdriver with logged in user. We do this so we don't have to do
    2-step authentication for every new course.

    """
    password = getpass.getpass()

    #driver = webdriver.PhantomJS(executable_path="node_modules/phantomjs/lib/phantom/bin/phantomjs")
    driver = webdriver.Chrome(executable_path="node_modules/chromedriver/lib/chromedriver/chromedriver")
    driver.get("https://myvideosu.stanford.edu")

    username_field = driver.find_element_by_name("username")
    username_field.send_keys(username)

    password_field = driver.find_element_by_name("password")
    password_field.send_keys(password)

    print "Logging in to myvideosu.stanford.edu..."
    driver.find_element_by_name("Submit").click()

    two_step_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "send"))
    )
    two_step_button.click()
    two_step_field = driver.find_element_by_name("otp")
    two_step_code = raw_input("Please enter 2-step authentication code: ")
    two_step_field.send_keys(two_step_code)
    driver.find_element_by_name("send").click()

    return driver

def get_course_url(course_name):
    """Get the course url from the course name.

    Parameters
    ----------
    course_name: str
        name of the course with format departmentPrefix + courseNumber
        (e.g. "cs106a")

    Return full course url.

    """
    # Add slash between dept prefix and course number for url creation. e.g.
    #       cs107  --> cs/107
    #       engr40 --> engr/40
    first_digit = re.search('\d', course_name).start()
    course_name = course_name[:first_digit] + '/' + course_name[first_digit:]
    return "%s/%s/%s/%s" % (DOWNLOAD_URL_PREFIX, QUARTER, YEAR, course_name)

def download_all_courses(username, course_names, download_settings):
    """Download all courses for the given user with the given settings."""
    driver = login(username)
    for course_name in course_names:
        download_course_lectures(driver, course_name, download_settings)
    driver.quit()

def parse_flags(flags):
    """Given a list of command-line flags, return a dictionary of download settings.

    flags: [str]
        list of command-line flags

    """
    download_settings = {
        "newestFirst": False,
        "outputPath":""
    }

    # parse flags
    for flag in flags:
        if flag == HELP_FLAG:
            print_help_documentation()
            sys.exit(0)
        elif flag == ALL_FLAG:
            # Append names of subdirectories (excluding hidden folders and 'watched') to courseNames list
            courseNames += [
                dir_name for dir_name in os.listdir(".")
                if os.path.isdir(dir_name) and not (dir_name.startswith('.') or dir_name is "watched")
            ]
        elif flag == NEW_FIRST_FLAG:
            download_settings["newestFirst"] = True
        elif flag.startswith(OUTPUT_PATH_FLAG):
            path = flag[flag.find('=') + 1:]
            if path[-1] != "/":
                # Make sure '/' added at end so that subdirectories and files can be appended
                path += "/"
            if not os.path.exists(path):
                # Escape spaces
                path = path.replace(" ", "\ ")
            if not os.path.exists(path):
                print path + " does not exist"
                sys.exit(0)
            download_settings["outputPath"] = path
        else:
            print flag + " ignored"
            continue

    return download_settings


def print_help_documentation():
    print "\n"
    print "=== SCPD Scrape Help==="
    print "https://github.com/jkeesh/scpd-scraper"
    print "Usage:"
    print "  python scrape.py [username] --flag1 ... --flagN courseName1 courseName2 ... courseNameN"
    print "Flags:"
    print "  " +      ALL_FLAG    + ": downloads all new videos based on names of subdirectories in addition to courses listed"
    print "  " +  NEW_FIRST_FLAG  + ": downloads the newest (most recent) videos first"
    print "  " + OUTPUT_PATH_FLAG + ": sets the location where vidoes will be saved (default to download into course name subdirectories)"
    print "\n"


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print "Incorrect usage."
        print_help_documentation()
    else:
        username = sys.argv[1]
        flags = [param for param in sys.argv[1:len(sys.argv)] if param.startswith('--')]
        course_names = [param for param in sys.argv[2:len(sys.argv)] if not param.startswith('--')]
        download_settings = parse_flags(flags)

        download_all_courses(username, course_names, download_settings)

