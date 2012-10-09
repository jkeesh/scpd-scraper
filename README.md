# SCPD Scraper

This program downloads scpd videos for a given class in the order
that they happened as a wmv, then converts them to a mp4. Each time 
the script is run, it will update to download all of the undownloaded
videos. 

This script is modified from the one by Ben Newhouse [https://github.com/newhouseb](https://github.com/newhouseb).

Unfortunately, there are lots of dependencies to get it up and running

1. BeautifulSoup for parsing: [http://www.crummy.com/software/BeautifulSoup/](http://www.crummy.com/software/BeautifulSoup/)
2. Mechanize for emulating a browser, [http://www.crummy.com/software/BeautifulSoup/](http://wwwsearch.sourceforge.net/mechanize/)
3. mimms for downloading video streams [apt-get install mimms]
4. (For Apple fanbois) Handbrake CLI, for converting to mp4: [http://handbrake.fr/downloads2.php](http://handbrake.fr/downloads2.php)

To run:
Change to your username
When prompted, type your password

Usage: 
    python scrape.py "Interactive Computer Graphics"


The way I use it is to keep a folder of videos, and once I have watched them, move them
into a subfolder called watched. So it also wont redowload files that are in a subfolder
called watched.
