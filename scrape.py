#!/usr/bin/env python
import re
import os
import sys
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

"""

See README for general documentation:

Dependencies: 
1. BeautifulSoup for parsing: [sudo easy_install beautifulsoup4] or [http://www.crummy.com/software/BeautifulSoup/](http://www.crummy.com/software/BeautifulSoup/)
2. Mechanize for emulating a browser: [sudo easy_install mechanize] or [http://wwwsearch.sourceforge.net/mechanize/](http://wwwsearch.sourceforge.net/mechanize/)
3. mimms for downloading video streams [sudo apt-get install mimms] or using MacPorts for Mac [http://www.macports.org/](http://www.macports.org/)
5. (optional- prevents scraper from crashing when notes are being used) html5lib parser for BeautifulSoup http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser

Usage: 
    python scrape.py [yourUserName] [optional flags] "Autumn/2014/CS/103" "Autumn/2014/CS/106x" ...

"""

DOWNLOAD_URL_PREFIX = "https://mvideox.stanford.edu/Graduate#/"

# Flags
ALL_FLAG = "--all"
ORGANIZE_FLAG = "--org"
HELP_FLAG = "--help"
NEW_FIRST_FLAG = "--priority=new"
OUTPUT_PATH_FLAG = "--outputPath="


def alreadyDownloaded(fileName, courseName, outputPath):
    """Check directories for the video to see if it's downloaded already.

    Parameters
    ----------
    fileName: str
        file name of the video (not full path, just name like "thevideo.mp4")
    courseName: str
        name of the course
    outputPath: str
        path to the video download location

    Return whether the video with the given file name was downloaded already.

    """
    directories = [
        outputPath + fileName,
        outputPath + courseName + "/" + fileName,
        outputPath + "watched/" + fileName
    ]
    return any(os.path.exists(directory) for directory in directory)

def download(videoUrl, destinationFileName, courseName, downloadSettings):
    """Download the video with the given url.

    Parameters
    ----------
    videoUrl: str
        url of the video to download
    destinationFileName: str
        name of the file to download the video to locally (e.g. "thevideo.mp4")
    courseName: str
        name of the course
    downloadSettings: dict
        dictionary of settings for the download

    """
    if alreadyDownloaded(destinationFileName, courseName, downloadSettings["outputPath"]):
        print "Already downloaded %s" % destinationFileName
        return

    print "Starting download for %s" % destinationFileName

    if downloadSettings["shouldOrganize"]:
        coursePath = courseName.replace(" ", "\ ") # spaces break command line navigation
        assertDirectoryExists(downloadSettings["outputPath"] + courseName)
        destinationFileName = downloadSettings["outputPath"] + coursePath + "/" + destinationFileName
    else:
        destinationFileName = downloadSettings["outputPath"] + destinationFileName

    os.system("mimms -c %s %s" % (videoUrl, destinationFileName))
            
    print "Finished", destinationFileName
    
def assertDirectoryExists(dir):
    """Check if a directory exists. Make one if not.

    Parameters
    ----------
    dir: str
        directory name to check

    """
    if not os.path.exists(dir):
        os.makedirs(dir)

def containsFormByName(browser, formName):
    """Check if the browser's page has a form with the given name.

    Parameters
    ----------
    browser: Browser
        the browser whose page to check
    formName: str
        name of the form to check

    """
    return formName in [form.name for form in browser.forms()]

def downloadAllLectures(browser, courseUrl, downloadSettings):
    """Download all the lectures for the course with the given url.

    Parameters
    ----------
    browser: Browser
        the browser to open the web page with
    courseUrl: str
        the *full* url of the course page (e.g. https://mvideox.stanford.edu/Graduate#/CourseDetail/Autumn/2014/AA/210A)
    downloadSettings: dict
        dictionary of settings for the download

    """
    # TODO get actual course name
    courseName = courseUrl

    browser.open(courseUrl)

    # TODO get correct links

    # Build up a list of lectures
    print '\n=== Starting "' + courseName + '" ==='
    print "Loading video links."
    links = []
    for link in browser.links(text="WMP"):
        links.append(re.search(r"'(.*)'",link.url).group(1))
    link_file = open('links.txt', 'w')

    # ENDTODO

    if not downloadSettings["newestFirst"]:
        links.reverse() # download the oldest ones first.

    print "Found %d links, getting video streams."%(len(links))
    videos = []
    for link in links:
        try:
            response = browser.open(link)
            soup = BeautifulSoup(response.read())
        except:
            print '\n'
            print "Error reading "+ link
            print 'If this error is unexpected, try installing the html5lib parser for BeautifulSoup. Pages with Notes stored on them have been known to crash when using an outdated parser'
            print 'you can find instructions on installing the html5lib at "http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser"'
            print '\n'
            continue

        # TODO get correct info (might already be right, but not sure)
        video = soup.find('source')['src']
        video = re.sub("http", "mms", video)
        video = video.replace(' ', '%20') # remove spaces, they break urls
        output_name = re.search(r"[a-z]+[0-9]+[a-z]?/[0-9]+",video).group(0).replace("/","_") #+ ".wmv"
        # ENDTODO

        link_file.write(video + '\n')

        videos.append((video, output_name + ".mp4"))

        print video
    link_file.close()

    print "Downloading %d video streams."%(len(videos))
    for video in videos:
        download(video[0], video[1], courseName, downloadSettings)
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

    # driver = webdriver.PhantomJS(executable_path="node_modules/phantomjs/lib/phantom/bin/phantomjs")
    driver = webdriver.Chrome(executable_path="node_modules/chromedriver/lib/chromedriver/chromedriver")
    driver.get("https://myvideosu.stanford.edu")

    username_field = driver.find_element_by_name("username")
    username_field.send_keys(username)

    password_field = driver.find_element_by_name("password")
    password_field.send_keys(password)

    # Open the course page for the title you're looking for 
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

    # This script gives us full access to all videos
    with open('scpd_full_access.js') as script:
        script_text = script.read()
    driver.execute_script(script_text)

    # Assert that the login was successful
    assert driver.find_elements_by_name("login") == 0, "Logged in successfully"

    return driver

def downloadAllCourses(username, courseUrls, downloadSettings):
    driver = login(username)
    # for courseUrl in courseUrls:
        # downloadAllLectures(browser, DOWNLOAD_URL_PREFIX + courseUrl, downloadSettings)
    driver.quit()


def printHelpDocumentation():
    print "\n"
    print "=== SCPD Scrape Help==="
    print "https://github.com/jkeesh/scpd-scraper"
    print "Usage:"
    print "  python scrape.py 'username' '--flag1' ... '--flagN' 'courseName1' 'courseName2' ... 'courseNameN'"
    print "Flags:"
    print "  " +      ALL_FLAG    + ": downloads all new videos based on names of subdirectories in addition to courses listed"
    print "  " +   ORGANIZE_FLAG  + ": auto-organize downloads into subdirectories titled with the course name"
    print "  " +  NEW_FIRST_FLAG  + ": downloads the newest (most recent) videos first"
    print "  " + OUTPUT_PATH_FLAG + ": sets the location where vidoes will be saved"
    print "Dependencies:" 
    print "  1. BeautifulSoup for parsing: [sudo easy_install beautifulsoup4] or [http://www.crummy.com/software/BeautifulSoup/](http://www.crummy.com/software/BeautifulSoup/)"
    print "  2. Mechanize for emulating a browser: [sudo easy_install mechanize] or [http://wwwsearch.sourceforge.net/mechanize/](http://wwwsearch.sourceforge.net/mechanize/)"
    print "  3. mimms for downloading video streams [sudo apt-get install mimms] or using MacPorts for Mac [http://www.macports.org/](http://www.macports.org/)"
    print "  5. (optional- prevents scraper from crashing when notes are being used) html5lib parser for BeautifulSoup http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser"
    print "\n"


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print "Incorrect usage: please enter 'python scrape.py " + HELP_FLAG + "' for help"
    else:
        username = sys.argv[1]
        flags = [param for param in sys.argv[1:len(sys.argv)] if param.startswith('--')]
        courseNames = [param for param in sys.argv[2:len(sys.argv)] if not param.startswith('--')]
        downloadSettings = {
            "shouldOrganize": False,
            "newestFirst": False,
            "outputPath":"./"
        }

        # parse flags
        for flag in flags:
            if flag == HELP_FLAG:
                printHelpDocumentation()
                sys.exit(0)
            elif flag == ALL_FLAG:
                # Append names of subdirectories (excluding hidden folders and 'watched') to courseNames list
                courseNames += [
                    dirName for dirName in os.listdir(".")
                    if os.path.isdir(dirName) and not (dirName.startswith('.') or dirName is "watched")
                ]
            elif flag == ORGANIZE_FLAG:
                downloadSettings["shouldOrganize"] = True
            elif flag == NEW_FIRST_FLAG:
                downloadSettings["newestFirst"] = True
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
                downloadSettings["outputPath"] = path
            else:
                print flag + " ignored"
                continue

        downloadAllCourses(username, courseNames, downloadSettings)

