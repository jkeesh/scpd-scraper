import re
import os
import sys
from getpass import *
from mechanize import Browser
from BeautifulSoup import BeautifulSoup

"""

This program downloads scpd videos for a given class in the order
that they happened as a wmv, then converts them to a mp4. Each time 
the script is run, it will update to download all of the undownloaded
videos. 

This script is modified from the one by Ben Newhouse (https://github.com/newhouseb).

Unfortunately, there are lots of dependencies to get it up and running
1. Handbrake CLI, for converting to mp4: http://handbrake.fr/downloads2.php
2. BeautifulSoup for parsing: http://www.crummy.com/software/BeautifulSoup/
3. Mechanize for emulating a browser, http://wwwsearch.sourceforge.net/mechanize/

To run:
Change to your username
When prompted, type your password

Usage: python scrape.py "Interactive Computer Graphics"

The way I use it is to keep a folder of videos, and once I have watched them, move them
into a subfolder called watched. So it also wont redowload files that are in a subfolder
called watched.


"""

def convertToMp4(wmv, mp4):
	print "Converting ", mp4
	os.system('HandBrakeCLI -i %s -o %s' % (wmv, mp4))

def download(work):
	# work[0] is url, work[1] is wmv, work[2] is mp4
	if os.path.exists(work[2]) or os.path.exists("watched/"+work[2]):
		print "Already downloaded", work[2]
		return

	print "Starting", work[1]
	os.system("mimms -c %s %s" % (work[0], work[1]))
	convertToMp4(work[1], work[2])
	print "Finished", work[1]

if __name__ == '__main__':	
	br = Browser()
	br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6; en-us) AppleWebKit/531.9 (KHTML, like Gecko) Version/4.0.3 Safari/531.9')]
	br.set_handle_robots(False)
	br.open("https://myvideosu.stanford.edu/oce/currentquarter.aspx")
	assert br.viewing_html()
	br.select_form(name="login")
	br["username"] = "jkeeshin" #Put your username here
	br["password"] = getpass()

	# Open the course page for the title you're looking for 
	response = br.submit()
	response = br.follow_link(text=sys.argv[1])
        #print response.read()	
	
	response = br.follow_link(text="HERE")
	print response.read()
	# Build up a list of lectures
	links = []
	for link in br.links(text="WMP"):
		links.append(re.search(r"'(.*)'",link.url).group(1))

	# So we download the oldest ones first.
	links.reverse()

	videos = []

	for link in links:
		response = br.open(link)
		soup = BeautifulSoup(response.read())
		video = soup.find('object', id='WMPlayer')['data']
		video = re.sub("http","mms",video)		
		output_name = re.search(r"[a-z]+[0-9]+[a-z]?/[0-9]+",video).group(0).replace("/","_") #+ ".wmv"
		output_wmv = output_name + ".wmv"
		output_mp4 = output_name + ".mp4"
		videos.append((video, output_wmv, output_mp4))

	for video in videos:
		download(video)

	print "complete"
