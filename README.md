#roominfo_checker
Checks and displays all the room occupancy for ETH Zurich campus. Currently only looks at rooms administered by the 
central ETH administration and ignores all department administered rooms.

It should be noted that I chose to omit following items from the git push:
- JavaScript Dependencies (I don't want to get into unnecessary legal trouble/Don't want to read the licences. Follow 
the HTML head to see where they would usually be stored)
  - jQuery 3.6.0
  - jQuery UI Touch-Punch
  - jQuery UI
  - jQuery DataTables 1.11.3 with FixedColumns and FixedHeader extension
- Python packages (Not sure which of these are actually necessary but I can't be bothered to go 
through the list and check)
  - Werkzeug
  - beautifulsoup4
  - certifi
  - chardet
  - idna
  - pip
  - requests
  - robobrowser
  - setuptools
  - six
  - soupsieve
  - urllib3
- Fonts (both found on fontesk.com, free for commercial use)
  - Karasuma Gothic Regular
  - Blatant Bold

I don't pretend any of the JS is well written (or the python for that matter). This is just a means to an end so that 
I can abandon rauminfo.ethz.ch once and for all.