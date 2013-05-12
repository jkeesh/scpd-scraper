# SCPD Scraper

This program downloads scpd videos for a given class in the order
that they happened as a wmv, then converts them to a mp4. Each time 
the script is run, it will update to download all of the undownloaded
videos. 

This script is modified from the one by Ben Newhouse [https://github.com/newhouseb](https://github.com/newhouseb).

Unfortunately, there are lots of dependencies to get it up and running

1. BeautifulSoup for parsing: [sudo easy_install beautifulsoup4] or [http://www.crummy.com/software/BeautifulSoup/](http://www.crummy.com/software/BeautifulSoup/)
2. Mechanize for emulating a browser: [sudo easy_install mechanize] or [http://wwwsearch.sourceforge.net/mechanize/](http://wwwsearch.sourceforge.net/mechanize/)
3. mimms for downloading video streams [sudo apt-get install mimms]
4. (For Apple fanbois who don't want .wmv output) Handbrake CLI, for converting to mp4: [http://handbrake.fr/downloads2.php](http://handbrake.fr/downloads2.php)

To run:
Change to your username
When prompted, type your password

Usage: 
    python scrape.py [yourUserName] [optional flags] "Interactive Computer Graphics" "Programming Abstractions" ...


The way I use it is to keep a folder of videos, and once I have watched them, move them
into a subfolder called watched. So it also wont redownload files that are in a subfolder
called watched.


#Flags
Any of the following flags (besides "--help") can be used in conjunction with listed coursenames
give information on usage:
	--help
download all new videos from courses held in subdirectories whose names match the courses:

	--all
organize videos by downloading them to folders whose names match the courses:

	--org
convert lecture videos to mp4:

	--mp4

#Example Calls
To download all videos as detailed by subdirectories as well as all videos in Interactive Computer Graphics and convert them to mp4

	python scrape.py tupacShakur --all --org --mp4 "Interactive Computer Graphics"
