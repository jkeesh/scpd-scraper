# SCPD Scraper


This program downloads scpd videos for a given class in the order
that they happened as an mp4. Each time 
the script is run, it will update to download all of the undownloaded
videos. 

This script is modified from the one by Ben Newhouse [https://github.com/newhouseb](https://github.com/newhouseb).

To get it up and running...

	pip install -r requirements.txt
	npm install

Usage: 
    python scrape.py [yourUserName] [optional flags] cs107 cs109 ...


The way I use it is to keep a folder of videos, and once I have watched them, move them
into a subfolder called watched. So it also won't redownload files that are in a subfolder
called watched.

# Flags
Any of the following flags (besides "--help") can be used in conjunction with listed coursenames

Give information on usage:

	--help

dDwnload all new videos from courses held in subdirectories whose names match the courses:

	--all

Download the newest lectures first:

	--priority=new

Designate output location of videos (default is subdirectory with name `course_name`):

	--outputPath=[directory]
